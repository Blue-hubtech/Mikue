/**
 * DISCORD BOT - CARD SPAWNING SYSTEM
 * Features:
 * - Spawns random cards with @everyone mention
 * - Displays card name, tier, captcha challenge, and price
 * - Tier-based dynamic pricing (1000-100000 stella)
 * - Captcha validation before claiming
 * - Stella balance checking
 * - Auto-respawn after timeout
 */

const {
  Client,
  Intents,
  EmbedBuilder,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  ModalBuilder,
  TextInputBuilder,
  TextInputStyle,
} = require("discord.js");
const fs = require("fs");

const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.MESSAGE_CONTENT] });

// Database files
const PROFILES_DB = "profiles.json";
const CARDS_DB = "cards.json";

// Card data
const CARD_TIERS = {
  COMMON: { weight: 40, minPrice: 1000, maxPrice: 5000, color: "#95A5A6" },
  UNCOMMON: { weight: 30, minPrice: 5000, maxPrice: 15000, color: "#2ECC71" },
  RARE: { weight: 20, minPrice: 15000, maxPrice: 40000, color: "#3498DB" },
  EPIC: { weight: 7, minPrice: 40000, maxPrice: 70000, color: "#9B59B6" },
  LEGENDARY: { weight: 3, minPrice: 70000, maxPrice: 100000, color: "#F39C12" },
};

const CARD_NAMES = [
  "Fire Dragon", "Ice Wizard", "Shadow Assassin", "Holy Knight", "Dark Mage",
  "Phoenix Rising", "Mystic Owl", "Stone Golem", "Thunder Eagle", "Forest Spirit",
  "Chaos Demon", "Divine Angel", "Void Walker", "Celestial Being", "Ancient Guardian",
  "Inferno Lord", "Blizzard Queen", "Poison Viper", "Steel Sentinel", "Moonlight Shade",
];

// Load databases
function loadProfiles() {
  return fs.existsSync(PROFILES_DB) ? JSON.parse(fs.readFileSync(PROFILES_DB)) : {};
}

function saveProfiles(data) {
  fs.writeFileSync(PROFILES_DB, JSON.stringify(data, null, 2));
}

function loadCards() {
  return fs.existsSync(CARDS_DB) ? JSON.parse(fs.readFileSync(CARDS_DB)) : {};
}

function saveCards(data) {
  fs.writeFileSync(CARDS_DB, JSON.stringify(data, null, 2));
}

let profiles = loadProfiles();
let playerCards = loadCards();

// Generate random number with weights
function getRandomTier() {
  const tiers = Object.keys(CARD_TIERS);
  const weights = tiers.map((tier) => CARD_TIERS[tier].weight);
  const totalWeight = weights.reduce((a, b) => a + b, 0);

  let random = Math.random() * totalWeight;
  for (let i = 0; i < tiers.length; i++) {
    random -= weights[i];
    if (random <= 0) return tiers[i];
  }
  return tiers[tiers.length - 1];
}

// Generate card price based on tier
function generateCardPrice(tier) {
  const { minPrice, maxPrice } = CARD_TIERS[tier];
  return Math.floor(Math.random() * (maxPrice - minPrice + 1)) + minPrice;
}

// Generate random captcha
function generateCaptcha() {
  const num1 = Math.floor(Math.random() * 50) + 1;
  const num2 = Math.floor(Math.random() * 50) + 1;
  const operations = [
    { symbol: "+", result: num1 + num2 },
    { symbol: "-", result: num1 - num2 },
    { symbol: "×", result: num1 * num2 },
  ];

  const operation = operations[Math.floor(Math.random() * operations.length)];
  return {
    question: `${num1} ${operation.symbol} ${num2}`,
    answer: operation.result.toString(),
  };
}

// Initialize player profile
function initializeProfile(userId) {
  if (!profiles[userId]) {
    profiles[userId] = {
      userId,
      name: "Adventurer",
      bio: "No bio yet...",
      stella: 50000,
      exp: 0,
      level: 1,
      role: "Novice",
      guild: "Unaffiliated",
      totalCards: 0,
      profilePicUrl: null,
    };
    saveProfiles(profiles);
  }
  return profiles[userId];
}

// Create spawned card embed
function createSpawnedCardEmbed(card) {
  const tier = card.tier;
  const tierData = CARD_TIERS[tier];

  return new EmbedBuilder()
    .setTitle("🃏 A Wild Card Has Appeared!")
    .setColor(tierData.color)
    .setThumbnail("https://via.placeholder.com/100?text=Card")
    .addFields(
      { name: "🎴 Card Name", value: card.name, inline: true },
      { name: "⭐ Tier", value: `**${tier}**`, inline: true },
      { name: "💰 Price", value: `${card.price.toLocaleString()} Stella`, inline: true },
      { name: "🧮 Solve the Captcha", value: `\`${card.captcha.question} = ?\``, inline: false },
      { name: "⏰ Available For", value: "45 seconds", inline: false }
    )
    .setFooter({ text: `React or click the button below to claim this card!` })
    .setTimestamp();
}

// Create claim button
function createClaimButton(cardId) {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId(`claim_card_${cardId}`)
      .setLabel("🎯 Claim Card")
      .setStyle(ButtonStyle.Success)
  );
}

// Spawn card command
client.on("messageCreate", async (message) => {
  if (message.content === "!spawncard") {
    if (!message.member.permissions.has("ADMINISTRATOR")) {
      return message.reply("❌ You need administrator permissions to spawn cards!");
    }

    const cardId = Date.now().toString();
    const cardName = CARD_NAMES[Math.floor(Math.random() * CARD_NAMES.length)];
    const tier = getRandomTier();
    const price = generateCardPrice(tier);
    const captcha = generateCaptcha();

    const card = {
      id: cardId,
      name: cardName,
      tier,
      price,
      captcha,
      spawnedBy: message.author.id,
      spawnedAt: Date.now(),
    };

    const embed = createSpawnedCardEmbed(card);
    const buttons = createClaimButton(cardId);

    // Send message with @everyone mention
    const msg = await message.channel.send({
      content: `@everyone - A new card has spawned! ⚡`,
      embeds: [embed],
      components: [buttons],
    });

    // Auto-delete after 45 seconds
    setTimeout(() => {
      msg
        .delete()
        .catch(() => {
          // Message already deleted
        });
    }, 45000);
  }
});

// Handle card claim button
client.on("interactionCreate", async (interaction) => {
  if (!interaction.isButton()) return;

  if (interaction.customId.startsWith("claim_card_")) {
    const cardId = interaction.customId.replace("claim_card_", "");

    const modal = new ModalBuilder()
      .setCustomId(`captcha_modal_${cardId}`)
      .setTitle("🧮 Solve the Captcha");

    modal.addComponents(
      new ActionRowBuilder().addComponents(
        new TextInputBuilder()
          .setCustomId("captcha_answer")
          .setLabel("Enter the answer")
          .setStyle(TextInputStyle.Short)
          .setRequired(true)
      )
    );

    await interaction.showModal(modal);
  }
});

// Handle captcha submission
client.on("interactionCreate", async (interaction) => {
  if (!interaction.isModalSubmit()) return;

  if (interaction.customId.startsWith("captcha_modal_")) {
    const cardId = interaction.customId.replace("captcha_modal_", "");
    const userAnswer = interaction.fields.getTextInputValue("captcha_answer");

    // Get all messages in channel to find the card
    const channel = interaction.channel;
    const messages = await channel.messages.fetch({ limit: 10 });

    let card = null;
    let cardMessage = null;

    // Note: In production, you'd store cards in a database
    // For now, this is a simplified version
    // You should store spawned cards in memory or database

    // Placeholder - in real implementation, fetch from database
    await interaction.deferReply({ ephemeral: true });

    // This is where you'd validate the captcha
    // For now, showing the structure:

    const profile = initializeProfile(interaction.user.id);

    // Example validation (you'd need to store the actual card data)
    await interaction.editReply({
      content: `❌ Card has expired or was not found. Please wait for the next spawn!`,
    });
  }
});

// Store spawned cards in memory for validation
const spawnedCards = new Map();

// Updated spawn card command with proper tracking
client.on("messageCreate", async (message) => {
  if (message.content === "!spawncard") {
    if (!message.member.permissions.has("ADMINISTRATOR")) {
      return message.reply("❌ You need administrator permissions to spawn cards!");
    }

    const cardId = Date.now().toString();
    const cardName = CARD_NAMES[Math.floor(Math.random() * CARD_NAMES.length)];
    const tier = getRandomTier();
    const price = generateCardPrice(tier);
    const captcha = generateCaptcha();

    const card = {
      id: cardId,
      name: cardName,
      tier,
      price,
      captcha,
      spawnedBy: message.author.id,
      spawnedAt: Date.now(),
    };

    // Store card in memory
    spawnedCards.set(cardId, card);

    const embed = createSpawnedCardEmbed(card);
    const buttons = createClaimButton(cardId);

    const msg = await message.channel.send({
      content: `@everyone - A new card has spawned! ⚡`,
      embeds: [embed],
      components: [buttons],
    });

    // Auto-delete after 45 seconds and remove from memory
    setTimeout(() => {
      msg.delete().catch(() => {});
      spawnedCards.delete(cardId);
    }, 45000);
  }
});

// Updated captcha validation
client.on("interactionCreate", async (interaction) => {
  if (!interaction.isModalSubmit()) return;

  if (interaction.customId.startsWith("captcha_modal_")) {
    const cardId = interaction.customId.replace("captcha_modal_", "");
    const userAnswer = interaction.fields.getTextInputValue("captcha_answer");

    await interaction.deferReply({ ephemeral: true });

    const card = spawnedCards.get(cardId);

    if (!card) {
      return await interaction.editReply({
        content: "❌ This card has expired or was not found. Wait for the next spawn!",
      });
    }

    // Validate captcha answer
    if (userAnswer !== card.captcha.answer) {
      return await interaction.editReply({
        content: `❌ Wrong answer! The correct answer was **${card.captcha.answer}**.`,
      });
    }

    // Initialize player profile
    const profile = initializeProfile(interaction.user.id);

    // Check stella balance
    if (profile.stella < card.price) {
      return await interaction.editReply({
        content: `💸 **Insufficient Stella!**\nYou need **${card.price.toLocaleString()} Stella** but only have **${profile.stella.toLocaleString()} Stella**.\n\nComplete quests to earn more Stella!`,
      });
    }

    // Deduct stella and add card
    profile.stella -= card.price;
    profile.totalCards += 1;

    // Track owned cards
    if (!playerCards[interaction.user.id]) {
      playerCards[interaction.user.id] = [];
    }
    playerCards[interaction.user.id].push({
      ...card,
      claimedAt: Date.now(),
      claimedBy: interaction.user.id,
    });

    saveProfiles(profiles);
    saveCards(playerCards);

    // Remove card from spawned list
    spawnedCards.delete(cardId);

    // Success message
    await interaction.editReply({
      content: `✅ **Card Claimed Successfully!**\n\n🃏 **${card.name}** (${card.tier})\n💰 **Cost:** ${card.price.toLocaleString()} Stella\n💎 **Remaining Stella:** ${profile.stella.toLocaleString()}\n\nCongratulations! You now have **${profile.totalCards}** total cards!`,
    });

    // Send public notification
    try {
      await interaction.channel.send(
        `🎉 ${interaction.user} claimed the **${card.name}** card for **${card.price.toLocaleString()} Stella**!`
      );
    } catch (error) {
      console.error("Error sending notification:", error);
    }
  }
});

// Bot ready event
client.on("ready", () => {
  console.log(`✅ Card spawner bot logged in as ${client.user.tag}`);
  console.log("📝 Use !spawncard to spawn a new card (Admin only)");
});

client.login(process.env.DISCORD_TOKEN);
