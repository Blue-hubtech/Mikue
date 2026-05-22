# 🚀 Complete Setup Guide

## Step-by-Step Installation

### 1️⃣ Download & Extract
1. Download all bot files
2. Extract to a folder (e.g., `Discord_bot`)
3. Open terminal/command prompt in that folder

### 2️⃣ Install Python Dependencies
```bash
pip install -r requirements.txt
```

**If you get errors:**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3️⃣ Get Your Discord Bot Token
1. Go to https://discord.com/developers/applications
2. Click **"New Application"** → Name it (e.g., "Miku Bot")
3. Go to **"Bot"** tab → Click **"Reset Token"** → Copy it
4. **IMPORTANT:** Enable these under "Privileged Gateway Intents":
   - ✅ Presence Intent
   - ✅ Server Members Intent  
   - ✅ Message Content Intent
5. Save changes!

### 4️⃣ Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create account if needed
3. Click **"Create new secret key"**
4. Copy the key (starts with `sk-...`)
5. **Note:** You may need to add $5+ credit to your account

### 5️⃣ Configure .env File
1. Rename `.env.example` to `.env`
2. Open `.env` in notepad/text editor
3. Paste your tokens:
```
DISCORD_TOKEN=paste_your_discord_token_here
OPENAI_API_KEY=paste_your_openai_key_here
```
4. Save the file

### 6️⃣ Create cogs Folder Structure
```bash
# Windows
mkdir cogs
type nul > cogs\__init__.py

# Mac/Linux
mkdir cogs
touch cogs/__init__.py
```

Then move these files INTO the `cogs/` folder:
- `cards.py`
- `economy.py`
- `games.py`
- `pokemon.py`
- `media.py`
- `profile.py`
- `utils.py`
- `moderation.py`
- `admin.py`

**Final structure should be:**
```
Discord_bot/
├── bot.py
├── database.py
├── ai_personality.py
├── .env
└── cogs/
    ├── __init__.py
    ├── cards.py
    ├── economy.py
    └── ... (all other cog files)
```

### 7️⃣ Import Cards
**Option A — Real Shoob Cards:**
```bash
python shoob_api_importer.py
```
Choose option **3** (100 cards)

**Option B — Anime Characters:**
```bash
python anilist_importer.py
```
Choose option **2** (500 cards)

### 8️⃣ Invite Bot to Your Server
1. Go back to https://discord.com/developers/applications
2. Select your application
3. Go to **"OAuth2"** → **"URL Generator"**
4. Check these scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
5. Check these bot permissions:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Use External Emojis
   - ✅ Add Reactions
   - (Optional for moderation: Ban Members, Kick Members, Manage Roles)
6. Copy the generated URL
7. Paste in browser → Select your server → Authorize

### 9️⃣ Start the Bot!
```bash
python bot.py
```

You should see:
```
✅  Shoob API enabled!
==================================================
🎤  Miku#1234 is online!
🌐  Connected to 1 guilds
==================================================
  ✅  Loaded cogs.cards
  ✅  Loaded cogs.economy
  ... (all cogs loading)
```

---

## ✅ Test It Works

In your Discord server:

1. **Test card spawning:**
   - Wait 15 minutes for auto-spawn, OR
   - Use `.spawn` (admin only)

2. **Test commands:**
   ```
   .help
   .daily
   .balance
   .profile
   ```

3. **Test Miku AI:**
   - Tag the bot: `@Miku hello!`
   - She should respond with personality!

---

## 🐛 Common Issues

### "ModuleNotFoundError: No module named 'discord'"
```bash
pip install discord.py
```

### "ModuleNotFoundError: No module named 'cogs'"
- Make sure `cogs/` folder exists
- Make sure `__init__.py` is inside it
- All cog files should be IN the cogs folder

### "discord.errors.LoginFailure: Improper token"
- Check `.env` file format (no quotes around token)
- Get a fresh token from Discord Developer Portal
- Make sure no extra spaces

### "OpenAI API error: Incorrect API key"
- Check `.env` has correct OPENAI_API_KEY
- Make sure key starts with `sk-`
- Verify key at https://platform.openai.com/api-keys

### Bot online but no cards
- Run `python shoob_api_importer.py` first
- Check `database.db` file exists
- Try `.spawn` command manually

### "Intents required" error
- Go to Discord Developer Portal
- Bot tab → Enable all Privileged Gateway Intents
- Save changes → restart bot

---

## 🎉 You're Done!

Your Miku bot should now be:
- ✅ Online in your server
- ✅ Spawning cards every 15 minutes  
- ✅ Responding to commands
- ✅ Chatting with Miku personality

Type `.help` to see all commands!

---

**Need more help?** Check the error message in your terminal — it usually tells you exactly what's wrong!
