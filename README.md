<h1 align="center">BioLink Protector Telegram Bot</h1>

<p align="center">
  <a href="https://github.com/strad-dev131/BioLink-Protector"><img src="https://img.shields.io/github/stars/strad-dev131/BioLink-Protector?color=blue&style=flat" alt="GitHub Repo stars"></a>
  <a href="https://github.com/strad-dev131/BioLink-Protector/issues"><img src="https://img.shields.io/github/issues/strad-dev131/BioLink-Protector" alt="GitHub issues"></a>
  <a href="https://github.com/strad-dev131/BioLink-Protector/pulls"><img src="https://img.shields.io/github/issues-pr/strad-dev131/BioLink-Protector" alt="GitHub pull requests"></a>
  <a href="https://github.com/strad-dev131/BioLink-Protector/graphs/contributors"><img src="https://img.shields.io/github/contributors/strad-dev131/BioLink-Protector?style=flat" alt="GitHub contributors"></a>
  <a href="https://github.com/strad-dev131/BioLink-Protector/network/members"><img src="https://img.shields.io/github/forks/strad-dev131/BioLink-Protector?style=flat" alt="GitHub forks"></a>
</p>

<p align="center">
  <em>BioLink Protector is a Telegram bot Script that automatically monitors user bios in group chats for links. If a link is found in a user's bio, the bot can warn the user, mute them, or ban them based on configurable settings. This bot helps maintain a clean and safe environment in your Telegram group chats.
</em>
</p>
<hr>

## Features

- Automatically checks user bios and message text for links when users post in the group.
- Configurable **warnings**, **mutes**, and **bans** for users with links in their bios or messages.
- **Whitelist** & **Unwhitelist** trusted members  
- **Cancel Warning** reset a user’s warnings  
- **Admin-only controls** with interactive inline keyboards

## 🎮 Demo Bot

Try it live: [@LinkXdetectorBot](https://t.me/LinkXdetectorBot)

## Requirements

Before you begin, ensure you have met the following requirements:

- Python 3.8 or higher

## Installation

```bash
git clone https://github.com/strad-dev131/BioLink-Protector
cd BioLink-Protector
pip install -r requirements.txt

```

## Configuration

1. Open the `config.py` file in your favorite text editor.  
2. Set the following values (or provide them as environment variables):  
   - **`API_ID`**: Your API ID from [my.telegram.org](https://my.telegram.org).  
   - **`API_HASH`**: Your API Hash from [my.telegram.org](https://my.telegram.org).  
   - **`BOT_TOKEN`**: The token you obtained from [@BotFather](https://t.me/BotFather).  
   - **`MONGO_URI`**: Your MongoDB connection string (e.g., from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)).  
   - **`OWNER_ID`**: Your Telegram numeric user ID to allow the privileged `/broadcast` command.  
   - Optional broadcast extras: **`BROADCAST_CHAT_IDS`** – comma-separated chat IDs to always include in `/broadcast` (e.g., `12345,-100987654321`).  
   - Spam protection tuning: **`SPAM_WINDOW_SEC`** and **`SPAM_MAX_MSG`** to control mass-spam detection window and threshold.  

## Deploy the Bot

```sh
python bio.py
```

## Usage

1. Add the bot to your group.  
2. Grant the bot **Admin** rights (delete & restrict).  
3. In-chat commands (admins only):  
   - `/config` → choose “Warn”, “Mute”, or “Ban” and set warn count  
   - `/free [reply|id]` → whitelist a user  
   - `/unfree [reply|id]` → remove from whitelist  
   - `/freelist` → view all whitelisted users  
   - `/stats` → show chat protection stats (mode, limit, counts)
4. General commands:  
   - `/ping` → check bot latency  
   - `/id` → show your ID and chat/replied user ID  
   - `/about` → bot info and helpful links  
5. **Owner-only command (PM to bot)**:
   - `/broadcast <text>` → sends a message to all groups registered with the bot (only works for `OWNER_ID`)
6. **Auto-scan:** When a non-whitelisted user posts, their bio and message text are checked—warn/mute/ban applies.  


✨ **Note**: Fork this repo, & Star ☀️ the repo if you liked it. and Share this repo with Proper Credit

## Author

- Name: Elite Sid
- Telegram: [@TeamXUpdate](https://t.me/TeamXUpdate)

Feel free to reach out if you have any questions or feedback.

---

## What's new in this build

- Smarter link detection:
  - http/https/ftp, www.*
  - bare domains and subdomains
  - IPv4/IPv6 addresses with optional ports
  - emails
  - Telegram @usernames
  - obfuscated formats: `dot`/`[.]`, `(dot)`, spaces in `://` and `www.`, zero‑width characters, `hxxp` → `http`, `t . me` → `t.me`
- Faster and more reliable:
  - Admin check optimized with get_chat_member + caching
  - Config and whitelist caching to reduce DB round-trips
  - Atomic warning increments with Mongo find_one_and_update
  - Optional uvloop for high-performance event loop on Linux/VPS
- 24×7 ready:
  - Works on any VPS (Docker and systemd examples below)
  - One-click deploy to Heroku and Render

## Deploy options

### Local/VPS (bare metal)
- Install dependencies
  - Python 3.12 recommended
  - MongoDB (Atlas connection also works)
- Set environment variables (or set values directly in config.py):
  - API_ID, API_HASH, BOT_TOKEN, MONGO_URI
- Run: `python bio.py`

### Docker
A Dockerfile is included. Build and run:

```bash
docker build -t biolink-protector .
docker run --rm -it \
  -e API_ID=12345 \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=12345:bot_token \
  -e MONGO_URI='mongodb+srv://...' \
  biolink-protector
```

### Heroku (1-click)
Use the button or the dashboard to deploy. Ensure all env vars are set.

[Deploy to Heroku](https://heroku.com/deploy?template=https://github.com/Yewsdhi/Biolinkbot)

### Render
A render.yaml is included. Create a Worker service:

- Build Command: `pip install -r requirements.txt`
- Start Command: `python bio.py`
- Add env vars: API_ID, API_HASH, BOT_TOKEN, MONGO_URI

### Systemd (VPS) example
Create `/etc/systemd/system/biolink-protector.service`:

```
[Unit]
Description=BioLink Protector Telegram Bot
After=network.target

[Service]
User=youruser
WorkingDirectory=/opt/biolink-protector
Environment=API_ID=12345
Environment=API_HASH=your_api_hash
Environment=BOT_TOKEN=12345:bot_token
Environment=MONGO_URI=mongodb+srv://...
ExecStart=/usr/bin/python3 /opt/biolink-protector/bio.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now biolink-protector
```
