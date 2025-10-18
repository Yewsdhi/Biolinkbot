from typing import Dict, Tuple, Set
import time

from pyrogram import Client, enums
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from config import (
    MONGO_URI,
    DEFAULT_CONFIG,
    DEFAULT_PUNISHMENT,
    DEFAULT_WARNING_LIMIT,
)

# Mongo
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["telegram_bot_db"]
warnings_collection = db["warnings"]
punishments_collection = db["punishments"]
whitelists_collection = db["whitelists"]

# In-memory caches with TTL to reduce DB and API load
_ADMIN_CACHE: Dict[Tuple[int, int], Tuple[bool, float]] = {}          # (chat_id, user_id) -> (is_admin, expires_at)
_CONFIG_CACHE: Dict[int, Tuple[Tuple[str, int, str], float]] = {}     # chat_id -> ((mode, limit, penalty), expires_at)
_WHITELIST_CACHE: Dict[int, Tuple[Set[int], float]] = {}              # chat_id -> (set(user_ids), expires_at)

ADMIN_TTL = 300.0        # 5 minutes
CONFIG_TTL = 600.0       # 10 minutes
WHITELIST_TTL = 300.0    # 5 minutes


def _now() -> float:
    return time.monotonic()


async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    """
    Fast admin check using get_chat_member and cache result for a short TTL.
    """
    key = (chat_id, user_id)
    cached = _ADMIN_CACHE.get(key)
    if cached and cached[1] > _now():
        return cached[0]

    try:
        member = await client.get_chat_member(chat_id, user_id)
        status = getattr(member, "status", None)
        is_adm = status in {enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR}
    except Exception:
        is_adm = False

    _ADMIN_CACHE[key] = (is_adm, _now() + ADMIN_TTL)
    return is_adm


async def get_config(chat_id: int):
    """
    Returns (mode, limit, penalty) with caching.
    """
    cached = _CONFIG_CACHE.get(chat_id)
    if cached and cached[1] > _now():
        return cached[0]

    doc = await punishments_collection.find_one({"chat_id": chat_id})
    if doc:
        cfg = (
            doc.get("mode", "warn"),
            int(doc.get("limit", DEFAULT_WARNING_LIMIT)),
            doc.get("penalty", DEFAULT_PUNISHMENT),
        )
    else:
        cfg = DEFAULT_CONFIG

    _CONFIG_CACHE[chat_id] = (cfg, _now() + CONFIG_TTL)
    return cfg


async def update_config(chat_id: int, mode=None, limit=None, penalty=None):
    update = {}
    if mode is not None:
        update["mode"] = mode
    if limit is not None:
        update["limit"] = int(limit)
    if penalty is not None:
        update["penalty"] = penalty

    if update:
        await punishments_collection.update_one(
            {"chat_id": chat_id},
            {"$set": update},
            upsert=True,
        )
        # Update cache
        current = await get_config(chat_id)
        new_cfg = (
            update.get("mode", current[0]),
            int(update.get("limit", current[1])),
            update.get("penalty", current[2]),
        )
        _CONFIG_CACHE[chat_id] = (new_cfg, _now() + CONFIG_TTL)


async def increment_warning(chat_id: int, user_id: int) -> int:
    """
    Atomically increment warning counter and return the updated count.
    Uses find_one_and_update to avoid an extra round-trip.
    """
    doc = await warnings_collection.find_one_and_update(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc.get("count", 1))


async def reset_warnings(chat_id: int, user_id: int):
    await warnings_collection.delete_one({"chat_id": chat_id, "user_id": user_id})


async def _load_whitelist(chat_id: int) -> Set[int]:
    cursor = whitelists_collection.find({"chat_id": chat_id})
    docs = await cursor.to_list(length=None)
    return {int(doc["user_id"]) for doc in docs}


async def is_whitelisted(chat_id: int, user_id: int) -> bool:
    cached = _WHITELIST_CACHE.get(chat_id)
    if cached and cached[1] > _now():
        return user_id in cached[0]

    wl = await _load_whitelist(chat_id)
    _WHITELIST_CACHE[chat_id] = (wl, _now() + WHITELIST_TTL)
    return user_id in wl


async def add_whitelist(chat_id: int, user_id: int):
    await whitelists_collection.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True,
    )
    cached = _WHITELIST_CACHE.get(chat_id)
    if cached and cached[1] > _now():
        cached[0].add(user_id)


async def remove_whitelist(chat_id: int, user_id: int):
    await whitelists_collection.delete_one({"chat_id": chat_id, "user_id": user_id})
    cached = _WHITELIST_CACHE.get(chat_id)
    if cached and cached[1] > _now():
        cached[0].discard(user_id)


async def get_whitelist(chat_id: int) -> list:
    cached = _WHITELIST_CACHE.get(chat_id)
    if cached and cached[1] > _now():
        return list(sorted(cached[0]))

    wl = await _load_whitelist(chat_id)
    _WHITELIST_CACHE[chat_id] = (wl, _now() + WHITELIST_TTL)
    return list(sorted(wl))
