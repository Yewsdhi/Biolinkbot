# Copyright (C) @SID_ELITE
# Channel: https://t.me/TeamXUpdate

import re
import os

# Get environment variables (required for Heroku / Render / VPS)
API_ID = int(os.environ.get("API_ID", "12345678"))  # Your Telegram API ID
API_HASH = os.environ.get("API_HASH", "12345678abcd")  # Your Telegram API Hash
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7267436522:XXXXXXXXXXXXXXXXXX")  # Your Bot Token

# Owner ID for privileged commands like /broadcast
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))  # Set this to your Telegram user ID

# MongoDB connection URI
MONGO_URI = os.environ.get("MONGO_URI", "your_mongodb_url")

# Optional: extra chat IDs to include in broadcasts (comma-separated ints)
# Example: BROADCAST_CHAT_IDS="12345,-100987654321"
_BROADCAST_CHAT_IDS = os.environ.get("BROADCAST_CHAT_IDS", "").strip()
BROADCAST_EXTRA_CHAT_IDS = []
if _BROADCAST_CHAT_IDS:
    for part in _BROADCAST_CHAT_IDS.split(","):
        part = part.strip()
        try:
            if part:
                BROADCAST_EXTRA_CHAT_IDS.append(int(part))
        except ValueError:
            # Ignore malformed entries
            pass

# Spam control configuration (to handle mass spamming)
SPAM_WINDOW_SEC = int(os.environ.get("SPAM_WINDOW_SEC", "8"))   # Sliding window in seconds
SPAM_MAX_MSG = int(os.environ.get("SPAM_MAX_MSG", "6"))         # Max messages allowed in window

DEFAULT_WARNING_LIMIT = 3
DEFAULT_PUNISHMENT = "mute"  # Options: "mute", "ban"
DEFAULT_CONFIG = ("warn", DEFAULT_WARNING_LIMIT, DEFAULT_PUNISHMENT)

# A robust URL/handle detector for bios:
# - http/https/ftp and www.* links
# - bare domains and IPs (with optional ports/paths)
# - emails
# - Telegram @usernames
URL_PATTERN = re.compile(
    r"""
    (?:                                             # Group of alternatives (no capture)
        (?:                                         # 1) URLs with scheme or www.
            (?:(?:https?|ftps?)://|www\.)[^\s'\"<>\(\)\[\]\{\}]+
        )
        |
        (?:                                         # 2) Bare domains/IP (with optional port/path)
            \b
            (?: 
                (?:[A-Za-z0-9-]{1,63}\.)+(?:[A-Za-z]{2,63})   # domain.tld
                |
                (?:\d{1,3}\.){3}\d{1,3}                       # IPv4
                |
                \[[0-9A-Fa-f:]+\]                             # [IPv6]
            )
            (?::\d{2,5})?
            (?:/[^\s'\"<>\(\)\[\]\{\}]*)?
        )
        |
        (?:                                         # 3) Emails
            \b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b
        )
        |
        (?:                                         # 4) Telegram usernames
            (?<!\w)@[\w_]{4,32}
        )
    )
    """,
    re.IGNORECASE | re.UNICODE | re.VERBOSE,
)
