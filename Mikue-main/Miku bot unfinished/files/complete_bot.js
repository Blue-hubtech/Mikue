/**
 * COMPLETE DISCORD BOT - PROFILE & CARD SYSTEM
 * Combined system for profile management and card spawning
 * Version: 2.0 - Production Ready
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

const client = new Client({
  intents: [
    Intents.FLAGS.GUILDS,
    Intents.FLAGS.GUILD_MEMBERS,
    Intents.FLAGS.MESSAGE_CONTENT,
  ],
});

// ============================================
// DATABASE CONFIGURATION
// ============================================

const PROFILES_DB = "profiles.json";
const CARDS_DB = "cards.json";

function loadProfiles() {
  return fs.existsSync(PROFILES_DB)
    ? JSON.parse(fs.readFileSync(PROFILES_DB))
    : {};
}

function saveProfiles(data) {
  fs.writeFileSync(PROFILES_DB, JSON.stringify(data, null, 2));
}

function loadCards() {
  return fs.existsSync(CARDS_DB)
    ? JSON.parse(fs.readFileSync(CARDS_DB))
    : {};
}

function saveCards(data) {
  fs.writeFileSync(CARDS_DB, JSON.stringify(data, null, 2));
}

let profiles = loadProfiles();
let playerCards = loadCards();
const spawnedCards = new Map();

// ============================================
// CARD SYSTEM CONFIGURATION
// ============================================

const CARD_TIERS = {
  COMMON: { weight: 40, minPrice: 1000, maxPrice: 5000, color: "#95A5A6" },
  UNCOMMON: { weight: 30, minPrice: 5000, maxPrice: 15000, color: "#2ECC71" },
  RARE: { weight: 20, minPrice: 15000, maxPrice: 40000, color: "#3498DB" },
  EPIC: { weight: 7, minPrice: 40000, maxPrice: 70000, color: "#9B59B6" },
  LEGENDARY: {
    weight: 3,
    minPrice: 70000,
    maxPrice: 100000,
    color: "#F39C12",
  },
};

const CARD_NAMES = [
  "Fire Dragon",
  "Ice Wizard",
  "Shadow Assassin",
  "Holy Knight",
  "Dark Mage",
  "Phoenix Rising",
  "Mystic Owl",
  "Stone Golem",
  "Thunder Eagle",
  "Forest Spirit",
  "Chaos Demon",
  "Divine Angel",
  "Void Walker",
  "Celestial Being",
  "Ancient Guardian",
  "Inferno Lord",
  "Blizzard Queen",
  "Poison Viper",
  "Steel Sentinel",
  "Moonlight Shade",
];

const CARD_SPAWN_TIME = 45000; // 45 seconds

// ============================================
// UTILITY FUNCTIONS
// ============================================

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
      createdAt: new Date().toISOString(),
    };
    saveProfiles(profiles);
  }
  return profiles[userId];
}

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

function generateCardPrice(tier) {
  const { minPrice, maxPrice } = CARD_TIERS[tier];
  return Math.floor(Math.random() * (maxPrice - minPrice + 1)) + minPrice;
}

function generateCaptcha() {
  const num1 = Math.floor(Math.random() * 50) + 1;
  const num2 = Math.floor(Math.random() * 50) + 1;
  const operations = [
    { symbol: "+", result: num1 + num2 },
    { symbol: "-", result: num1 - num2 },
    { symbol: "×", result: num1 * num2 },
  ];

  const operation =
    operations[Math.floor(Math.random() * operations.length)];
  return {
    question: `${num1} ${operation.symbol} ${num2}`,
    answer: operation.result.toString(),
  };
}

// ============================================
// PROFILE SYSTEM FUNCTIONS
// ============================================

function createProfileEmbed(userId) {
  const profile = initializeProfile(userId);

  const embed = new EmbedBuilder()
    .setTitle(`${profile.name}'s Profile`)
    .setColor("#FFD700")
    .setThumbnail(
      profile.profilePicUrl || "https://via.placeholder.com/200?text=No+Avatar"
    )
    .addFields(
      { name: "📝 Bio", value: profile.bio, inline: false },
      { name: "⭐ Level", value: `${profile.level}`, inline: true },
      { name: "💎 Stella", value: `${profile.stella.toLocaleString()}`, inline: true },
      { name: "🎯 Experience", value: `${profile.exp.toLocaleString()}`, inline: true },
      { name: "👤 Role", value: profile.role, inline: true },
      { name: "🏰 Guild", value: profile.guild, inline: true },
      { name: "🃏 Total Cards", value: `${profile.totalCards}`, inline: true }
    )
    .setFooter({ text: `Profile ID: ${userId}` })
    .setTimestamp();

  return embed;
}

function createProfileButtons(userId) {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId(`profile_pic_${userId}`)
      .setLabel("🖼️ Change Avatar")
      .setStyle(ButtonStyle.Primary),
    new ButtonBuilder()
      .setCustomId(`profile_bio_${userId}`)
      .setLabel("📝 Edit Bio")
      .setStyle(ButtonStyle.Secondary),
    new ButtonBuilder()
      .setCustomId(`profile_reset_pic_${userId}`)
      .setLabel("🔄 Reset Avatar")
      .setStyle(ButtonStyle.Danger)
  );
}

// ============================================
// CARD SYSTEM FUNCTIONS
// ============================================

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
    .setFooter({ text: "Click the button below to claim this card!" })
    .setTimestamp();
}

function createClaimButton(cardId) {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId(`claim_card_${cardId}`)
      .setLabel("🎯 Claim Card")
      .setStyle(ButtonStyle.Success)
  );
}

// ============================================
// EVENT HANDLERS - READY
// ============================================

client.on("ready", async () => {
  console.log(`✅ Bot logged in as ${client.user.tag}`);

  const commands = [
    {
      name: "profile",
      description: "View your profile or another user's profile",
      options: [
        {
          type: 6,
          name: "user",
          description: "User to view (defaults to yourself)",
          required: false,
        },
      ],
    },
  ];

  try {
    await client.application.commands.set(commands);
    console.log("✅ Slash commands registered");
    console.log("📝 Text commands: !spawncard (admin)");
  } catch (error) {
    console.error("Error registering commands:", error);
  }
});

// ============================================
// EVENT HANDLERS - SLASH COMMANDS
// ============================================

client.on("interactionCreate", async (interaction) => {
  if (interaction.isCommand() && interaction.commandName === "profile") {
    const targetUser = interaction.options.getUser("user") || interaction.user;
    initializeProfile(targetUser.id);

    const embed = createProfileEmbed(targetUser.id);
    const buttons = createProfileButtons(targetUser.id);

    await interaction.reply({
      embeds: [embed],
      components: [buttons],
      ephemeral: false,
    });
  }
});

// ============================================
// EVENT HANDLERS - MESSAGE COMMANDS
// ============================================

client.on("messageCreate", async (message) => {
  // Ignore bot messages
  if (message.author.bot) return;

  // !spawncard command (admin only)
  if (message.content === "!spawncard") {
    if (!message.member.permissions.has("ADMINISTRATOR")) {
      return message.reply(
        "❌ You need **Administrator** permissions to spawn cards!"
      );
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

    spawnedCards.set(cardId, card);

    const embed = createSpawnedCardEmbed(card);
    const buttons = createClaimButton(cardId);

    const msg = await message.channel.send({
      content: `@everyone - A new card has spawned! ⚡`,
      embeds: [embed],
      components: [buttons],
    });

    // Auto-delete after timeout
    setTimeout(() => {
      msg.delete().catch(() => {});
      spawnedCards.delete(cardId);
    }, CARD_SPAWN_TIME);
  }
});

// ============================================
// EVENT HANDLERS - BUTTONS
// ============================================

client.on("interactionCreate", async (interaction) => {
  if (!interaction.isButton()) return;

  // Profile button: Change Avatar
  if (interaction.customId.startsWith("profile_pic_")) {
    const userId = interaction.customId.replace("profile_pic_", "");

    const modal = new ModalBuilder()
      .setCustomId(`profile_modal_pic_${userId}`)
      .setTitle("Update Profile Picture");

    modal.addComponents(
      new ActionRowBuilder().addComponents(
        new TextInputBuilder()
          .setCustomId("pic_url")
          .setLabel("Image URL")
          .setStyle(TextInputStyle.Short)
          .setPlaceholder("https://example.com/image.png")
          .setRequired(true)
      )
    );

    await interaction.showModal(modal);
  }

  // Profile button: Edit Bio
  if (interaction.customId.startsWith("profile_bio_")) {
    const userId = interaction.customId.replace("profile_bio_", "");

    const modal = new ModalBuilder()
      .setCustomId(`profile_modal_bio_${userId}`)
      .setTitle("Update Bio");

    modal.addComponents(
      new ActionRowBuilder().addComponents(
        new TextInputBuilder()
          .setCustomId("bio_text")
          .setLabel("Your Bio (Max 200 characters)")
          .setStyle(TextInputStyle.Paragraph)
          .setMaxLength(200)
          .setRequired(true)
      )
    );

    await interaction.showModal(modal);
  }

  // Profile button: Reset Avatar
  if (interaction.customId.startsWith("profile_reset_pic_")) {
    const userId = interaction.customId.replace("profile_reset_pic_", "");
    profiles[userId].profilePicUrl = null;
    saveProfiles(profiles);

    const embed = createProfileEmbed(userId);
    const buttons = createProfileButtons(userId);

    await interaction.update({
      embeds: [embed],
      components: [buttons],
    });
  }

  // Card button: Claim Card
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

// ============================================
// EVENT HANDLERS - MODALS
// ============================================

client.on("interactionCreate", async (interaction) => {
  if (!interaction.isModalSubmit()) return;

  // Profile modal: Update Picture
  if (interaction.customId.startsWith("profile_modal_pic_")) {
    const userId = interaction.customId.replace("profile_modal_pic_", "");
    const picUrl = interaction.fields.getTextInputValue("pic_url");

    try {
      new URL(picUrl);
      profiles[userId].profilePicUrl = picUrl;
      saveProfiles(profiles);

      const embed = createProfileEmbed(userId);
      const buttons = createProfileButtons(userId);

      await interaction.update({
        embeds: [embed],
        components: [buttons],
      });
    } catch (error) {
      await interaction.reply({
        content: "❌ Invalid URL. Please provide a valid image URL.",
        ephemeral: true,
      });
    }
  }

  // Profile modal: Update Bio
  if (interaction.customId.startsWith("profile_modal_bio_")) {
    const userId = interaction.customId.replace("profile_modal_bio_", "");
    const bioText = interaction.fields.getTextInputValue("bio_text");

    profiles[userId].bio = bioText;
    saveProfiles(profiles);

    const embed = createProfileEmbed(userId);
    const buttons = createProfileButtons(userId);

    await interaction.update({
      embeds: [embed],
      components: [buttons],
    });
  }

  // Card modal: Validate Captcha
  if (interaction.customId.startsWith("captcha_modal_")) {
    const cardId = interaction.customId.replace("captcha_modal_", "");
    const userAnswer =
      interaction.fields.getTextInputValue("captcha_answer");

    await interaction.deferReply({ ephemeral: true });

    const card = spawnedCards.get(cardId);

    // Card expired or not found
    if (!card) {
      return await interaction.editReply({
        content:
          "❌ **Card Expired!**\nThis card has expired or was not found. Wait for the next spawn!",
      });
    }

    // Wrong captcha answer
    if (userAnswer !== card.captcha.answer) {
      return await interaction.editReply({
        content: `❌ **Wrong Answer!**\nThe correct answer was **${card.captcha.answer}**.`,
      });
    }

    // Initialize and get profile
    const profile = initializeProfile(interaction.user.id);

    // Check stella balance
    if (profile.stella < card.price) {
      return await interaction.editReply({
        content: `💸 **Insufficient Stella!**\nYou need **${card.price.toLocaleString()} Stella** but only have **${profile.stella.toLocaleString()} Stella**.\n\n💡 Complete quests and challenges to earn more Stella!`,
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
      content: `✅ **Card Claimed Successfully!**\n\n🃏 **${card.name}** (${card.tier})\n💰 **Cost:** ${card.price.toLocaleString()} Stella\n💎 **Remaining Stella:** ${profile.stella.toLocaleString()}\n📊 **Total Cards:** ${profile.totalCards}`,
    });

    // Public notification
    try {
      await interaction.channel.send(
        `🎉 ${interaction.user} claimed the **${card.name}** card for **${card.price.toLocaleString()} Stella**!`
      );
    } catch (error) {
      console.error("Error sending notification:", error);
    }
  }
});

// ============================================
// ERROR HANDLING
// ============================================

client.on("error", (error) => {
  console.error("Client error:", error);
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
});

// ============================================
// START BOT
// ============================================

client.login(process.env.DISCORD_TOKEN);
