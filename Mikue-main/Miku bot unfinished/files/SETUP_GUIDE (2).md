
# 🎮 Player Profile & Card Spawning System - Complete Documentation

## 📋 Overview

This is a complete Discord bot system featuring:
1. **Player Profile System** - Profile management with avatars, bio, and stats
2. **Card Spawning System** - Dynamic card spawning with captcha and pricing

---

## 🚀 Installation & Setup

### Prerequisites
- Node.js (v16+)
- Discord Bot with intents enabled
- discord.js v14+

### Install Dependencies
```bash
npm install discord.js dotenv
```

### Environment Setup
Create a `.env` file:
```
DISCORD_TOKEN=your_bot_token_here
```

### File Structure
```
your-bot/
├── profile_system.js
├── card_spawning_system.js
├── .env
├── profiles.json (auto-created)
├── cards.json (auto-created)
└── package.json
```

---

## 👤 PROFILE SYSTEM

### Features

✅ **Profile Picture Management**
- Upload custom avatar via URL
- Reset to default placeholder
- Profile pictures displayed in embeds

✅ **Bio Editor**
- Edit custom bio up to 200 characters
- Modal-based input system
- Instant updates

✅ **Player Stats Display**
- Level and Experience
- Stella balance
- Role and Guild affiliation
- Total cards owned
- Account creation date

✅ **Data Persistence**
- All data saved to JSON database
- Auto-initialization for new players
- Profile history tracking

### Commands

#### `/profile [user]`
View a player's profile or your own
```
/profile @username
/profile (defaults to yourself)
```

**Profile Display Includes:**
- 🖼️ Avatar/Profile Picture
- 📝 Bio Information
- ⭐ Current Level
- 💎 Stella Balance
- 🎯 Total Experience
- 👤 Player Role
- 🏰 Guild Name
- 🃏 Total Cards Owned

### Profile Buttons

| Button | Function |
|--------|----------|
| 🖼️ Change Avatar | Upload new profile picture via URL |
| 📝 Edit Bio | Edit your bio (max 200 chars) |
| 🔄 Reset Avatar | Remove current avatar, return to default |

### Profile Data Structure
```json
{
  "userId": "discord_id",
  "name": "Adventurer",
  "bio": "User bio text",
  "stella": 5000,
  "exp": 0,
  "level": 1,
  "role": "Novice",
  "guild": "Unaffiliated",
  "totalCards": 0,
  "profilePicUrl": "https://...",
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

### How to Integrate Profile Stats Updates

Update player stats in your other commands:

```javascript
const profile = profiles[userId];
profile.stella += 100; // Add stella
profile.exp += 50; // Add exp
profile.totalCards += 1; // Add card
profile.level = Math.floor(profile.exp / 1000) + 1; // Auto-calculate level
saveProfiles(profiles);
```

---

## 🃏 CARD SPAWNING SYSTEM

### Features

✅ **Dynamic Card Spawning**
- 5 rarity tiers (Common → Legendary)
- Weighted random selection
- Automatic @everyone mentions

✅ **Tier-Based Pricing System**

| Tier | Rarity | Weight | Price Range | Color |
|------|--------|--------|-------------|-------|
| COMMON | ⬜ | 40% | 1,000-5,000 | Gray |
| UNCOMMON | 🟢 | 30% | 5,000-15,000 | Green |
| RARE | 🔵 | 20% | 15,000-40,000 | Blue |
| EPIC | 🟣 | 7% | 40,000-70,000 | Purple |
| LEGENDARY | 🟠 | 3% | 70,000-100,000 | Orange |

✅ **Captcha Validation**
- Random math problems (addition, subtraction, multiplication)
- Player must solve to claim card
- Wrong answers rejected automatically

✅ **Stella Validation**
- Check if player has sufficient balance
- Custom error message if insufficient funds
- Automatic deduction upon successful claim

✅ **Auto-Expiration**
- Cards disappear after 45 seconds
- Players receive notification of expiration
- Card automatically removed from claims list

✅ **Claim Notification**
- Public message when card is claimed
- Shows card name, tier, price, and claimer
- Updates player's total card count

### Commands

#### `!spawncard` (Admin Only)
Spawns a new card in the current channel
```
!spawncard
```

**Requirements:**
- Administrator permissions required
- Card appears with @everyone mention
- 45-second timer until auto-deletion

### Card Spawn Message Format

When a card spawns:
```
@everyone - A new card has spawned! ⚡

🃏 A Wild Card Has Appeared!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎴 Card Name: Fire Dragon
⭐ Tier: RARE
💰 Price: 25,000 Stella
🧮 Solve the Captcha: 42 × 3 = ?
⏰ Available For: 45 seconds
```

### Claiming a Card - User Flow

1. **View spawned card** with @everyone mention
2. **Click "🎯 Claim Card" button**
3. **Modal appears** asking for captcha answer
4. **Submit answer**
   - ✅ Correct: Stella deducted, card added
   - ❌ Wrong: Notification of correct answer
   - 💸 Insufficient funds: "Insufficient Stella" message

### Error Messages

**Card Expired:**
```
❌ This card has expired or was not found. Wait for the next spawn!
```

**Wrong Captcha Answer:**
```
❌ Wrong answer! The correct answer was 42.
```

**Insufficient Stella:**
```
💸 Insufficient Stella!
You need 25,000 Stella but only have 15,000 Stella.

Complete quests to earn more Stella!
```

**Success Message:**
```
✅ Card Claimed Successfully!

🃏 Fire Dragon (RARE)
💰 Cost: 25,000 Stella
💎 Remaining Stella: 75,000

Congratulations! You now have 5 total cards!
```

**Public Notification:**
```
🎉 @username claimed the Fire Dragon card for 25,000 Stella!
```

### Card Data Structure
```json
{
  "id": "1234567890",
  "name": "Fire Dragon",
  "tier": "RARE",
  "price": 25000,
  "captcha": {
    "question": "42 × 3",
    "answer": "126"
  },
  "spawnedBy": "bot_id",
  "spawnedAt": 1704067200000,
  "claimedBy": "user_id",
  "claimedAt": 1704067230000
}
```

---

## 🔧 Integration Guide

### Running Both Systems Together

**Option 1: Single Bot File (Recommended)**

Combine both systems in one bot:

```javascript
// bot.js
const profileSystem = require('./profile_system.js');
const cardSpawner = require('./card_spawning_system.js');

// Both systems work together seamlessly
```

**Option 2: Separate Bots**

Run as separate bots on different tokens (for scalability).

### Updating Player Stats

Whenever player stats change, use:

```javascript
// Get profile
const profile = profiles[userId];

// Update any stat
profile.stella += amount;
profile.exp += amount;
profile.level = Math.floor(profile.exp / 1000) + 1;
profile.totalCards += 1;
profile.role = "Legendary";
profile.guild = "Dragon Slayers";

// Save
saveProfiles(profiles);
```

### Adding More Cards

Add card names to the list:

```javascript
const CARD_NAMES = [
  "Fire Dragon", "Ice Wizard", "Shadow Assassin",
  // Add more here
  "Your Custom Card Name",
];
```

### Adjusting Pricing

Modify tier prices:

```javascript
const CARD_TIERS = {
  COMMON: { weight: 40, minPrice: 2000, maxPrice: 8000, color: "#95A5A6" },
  // Adjust min and max as needed
};
```

### Adjusting Spawn Time

Change card availability duration (in milliseconds):

```javascript
// Currently 45 seconds (45000 ms)
setTimeout(() => {
  msg.delete();
  spawnedCards.delete(cardId);
}, 45000); // Change this value
```

---

## 📊 Database Files

### profiles.json
Stores all player profile data

**Example:**
```json
{
  "123456789": {
    "userId": "123456789",
    "name": "Adventurer",
    "bio": "Love collecting cards!",
    "stella": 50000,
    "exp": 5000,
    "level": 6,
    "role": "Hero",
    "guild": "Card Collectors",
    "totalCards": 12,
    "profilePicUrl": "https://..."
  }
}
```

### cards.json
Stores all claimed cards by player

**Example:**
```json
{
  "123456789": [
    {
      "id": "1704067230000",
      "name": "Fire Dragon",
      "tier": "RARE",
      "price": 25000,
      "claimedAt": 1704067230000
    }
  ]
}
```

---

## ⚙️ Advanced Customization

### Custom Card Tiers

Add new tiers or modify existing:

```javascript
const CARD_TIERS = {
  MYTHICAL: { weight: 1, minPrice: 100000, maxPrice: 150000, color: "#FF00FF" },
  // ...existing tiers
};
```

### Custom Captcha Types

Add different math operations or puzzle types:

```javascript
function generateCaptcha() {
  const operations = [
    { symbol: "+", calc: (a, b) => a + b },
    { symbol: "-", calc: (a, b) => a - b },
    { symbol: "÷", calc: (a, b) => Math.floor(a / b) },
    // Add more operations
  ];
  // ...
}
```

### Profile Filtering & Search

Add commands to search players:

```javascript
client.on("messageCreate", async (message) => {
  if (message.content.startsWith("!searchplayer")) {
    const playerName = message.content.replace("!searchplayer ", "");
    const results = Object.values(profiles).filter(p => 
      p.name.toLowerCase().includes(playerName.toLowerCase())
    );
    // Display results
  }
});
```

---

## 🐛 Troubleshooting

### Bot Won't Start
- Check `.env` file has valid token
- Verify discord.js is installed: `npm list discord.js`

### Commands Not Showing
- Use `/sync` to register slash commands
- Check bot has "applications.commands" scope in OAuth2

### Database Errors
- Delete corrupted JSON files and restart bot
- Check file permissions (should be writable)

### Captcha Always Shows Wrong
- Verify `generateCaptcha()` function math is correct
- Check answer storage in `spawnedCards.set()`

---

## 📈 Future Enhancements

**Potential Additions:**
- Trading system between players
- Card rarity effects (stat bonuses)
- Leaderboards
- Daily card spawn limits
- Card evolution/upgrade system
- Battle system using collected cards
- Achievements and badges
- Weekly card raffles

---

## 💡 Tips & Best Practices

1. **Backup your databases** regularly
2. **Test captcha logic** with edge cases (negative numbers, zero)
3. **Monitor bot latency** during peak card spawning
4. **Set reasonable spawn frequency** (suggested: 30-60 min intervals)
5. **Use role-based access** for admin spawn commands
6. **Log all transactions** for debugging

---

## 📝 License & Support

This system is provided as-is. Modify and customize as needed for your Discord server!

For questions or improvements, refer to discord.js documentation:
https://discord.js.org/docs

---

**Last Updated:** January 2025
**Version:** 2.0
**Status:** Production Ready ✅
