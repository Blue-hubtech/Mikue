# 🎤 Miku's Card Collection Bot

A feature-rich Discord bot with Hatsune Miku personality, card collecting, economy system, Pokémon, games, and more!

## ✨ Features

### 🎴 Card System
- **Real Shoob cards** via API integration
- Auto-spawning every 15 minutes
- 6 rarity tiers (Common → Mythic)
- Collection tracking & trading
- Card marketplace
- Duplicate merging for Stellas

### 💫 Economy System
- Daily & weekly rewards
- Casino games (slots, dice, roulette)
- Rob other players
- Gift Stellas to friends
- Item shop & currency conversion
- Card packs (100 Stellas each)

### ⚡ Pokémon System
- Catch wild Pokémon
- Battle other trainers
- Party & PC storage
- Pokédex with 12+ Pokémon
- Healing & move learning
- Rarity-based catching

### 🎮 Games
- Anime quiz with rewards
- Hangman
- Chess challenges (coming soon)

### 🎵 Music & Media
- **Deezer** — search songs, artists, albums (NO API KEY!)
- **YouTube** — search videos & music
- Song lyrics lookup
- Social media downloaders (TikTok, Instagram, etc.)

### 👤 Profile System
- Custom bios & usernames
- Profile icons
- XP & leveling system
- Rank display with progress bars
- Profile locking

### 🔧 Utility Tools
- AI chat with Miku personality
- Weather lookup
- Dictionary definitions
- Horoscopes
- Translation tools
- Emoji mixing

### 🛡️ Moderation
- Ban, kick, mute, warn
- Role management (promote/demote)
- Channel control (open/close)
- Command enable/disable

### 👑 Admin Commands
- Add/edit/remove cards
- Give Stellas & gems to users
- Adjust daily reward amounts
- Manual card spawning
- User data management

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- Discord bot account ([create one here](https://discord.com/developers/applications))
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### 2. Installation

```bash
# Clone or download the bot files
cd Discord_bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your DISCORD_TOKEN and OPENAI_API_KEY
```

### 3. Import Cards

**Option A: Real Shoob Cards (Recommended)**
```bash
python shoob_api_importer.py
# Choose option 3 (100 cards)
```

**Option B: AniList Anime Characters**
```bash
python anilist_importer.py
# Choose option 2 (500 cards)
```

### 4. Start the Bot
```bash
python bot.py
```

---

## 📋 Commands

Use `.help` in Discord to see all commands, or `.help <category>` for specific categories:

- `.help cards` — Card collecting commands
- `.help economy` — Stellas & casino
- `.help games` — Fun games
- `.help pokemon` — Pokémon system
- `.help media` — Music & downloads
- `.help profile` — Customize your profile
- `.help utils` — Utility tools
- `.help moderation` — Server moderation
- `.help admin` — Owner commands

### Quick Commands
```
.daily          — Claim daily Stellas
.collection     — View your cards
.pokemon        — View your Pokémon
.balance        — Check your Stellas
.profile        — View your profile
.song <query>   — Search songs on Deezer
.quiz           — Start an anime quiz
```

---

## 🎨 Card Generator (Optional)

Create custom card designs:

```bash
python card_generator.py
```

Drop your character images in:
```
card_images/
├── Common/
├── Uncommon/
├── Rare/
├── Epic/
├── Legendary/
└── Mythic/
```

File format: `SeriesName - CharacterName.png`

The generator creates sleek modern cards with:
- Glowing borders by rarity
- Gradient backgrounds
- Tier badges (TIER I → TIER VI)
- Star ratings
- Character descriptions

---

## 🔑 API Keys (Optional)

### Required
- **Discord Token** — Bot authentication
- **OpenAI API Key** — Miku's AI personality

### Optional (Free)
- **YouTube API** — Enhanced video/music search
- **Genius API** — Song lyrics

All optional APIs improve features but the bot works without them!

---

## 🎤 Miku's Personality

The bot uses GPT-4o-mini to give Miku a dynamic personality:
- Responds when @mentioned or replied to
- Energetic virtual idol character
- Uses Japanese expressions (sugoi, nani, yatta)
- Gets more excited for rare cards
- Music & singing metaphors
- Rotating status messages

---

## 📁 File Structure

```
Discord_bot/
├── bot.py                  # Main bot file
├── database.py             # Database operations
├── ai_personality.py       # Miku's AI responses
├── requirements.txt        # Python dependencies
├── .env                    # Your API keys (create from .env.example)
│
├── shoob_api_importer.py   # Import real Shoob cards
├── anilist_importer.py     # Import anime characters
├── card_generator.py       # Create custom cards
├── card_loader.py          # Bulk load from folders
│
└── cogs/                   # Command modules
    ├── cards.py
    ├── economy.py
    ├── games.py
    ├── pokemon.py
    ├── media.py
    ├── profile.py
    ├── utils.py
    ├── moderation.py
    └── admin.py
```

---

## 🐛 Troubleshooting

### Bot won't start
- Check `.env` file has correct DISCORD_TOKEN
- Verify you enabled all Intents in Discord Developer Portal
- Run `pip install -r requirements.txt` again

### No cards spawning
- Import cards first: `python shoob_api_importer.py`
- Or use: `python anilist_importer.py`
- Check database.db file exists

### AI responses not working
- Verify OPENAI_API_KEY in `.env`
- Check OpenAI account has credits
- View console for error messages

### ModuleNotFoundError: No module named 'cogs'
- Create `cogs/` folder
- Add empty `__init__.py` file inside it
- Put all cog files in the folder

---

## 💡 Tips

- Cards auto-spawn every **15 minutes**
- Use `.daily` every 24 hours for free Stellas
- Tag Miku or reply to her messages to chat!
- Use `.roll` (100 Stellas) for random card packs
- Merge duplicate cards with `.merge` for Stellas
- Deezer music search needs NO API key!

---

## 📝 License

This bot is for personal/private use. Card images from Shoob API remain property of their respective owners.

---

## 🎉 Credits

- Built with discord.py
- Miku personality powered by OpenAI
- Card data from Shoob API & AniList
- Music data from Deezer API

---

**Enjoy your Miku bot!** 🎤💚

For support, check the error messages in console or review the troubleshooting section above.
