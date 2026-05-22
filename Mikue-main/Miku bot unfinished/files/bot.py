import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv
from database import Database
from ai_personality import get_ai_response, get_spawn_message, get_claim_message
from ranks import get_rank_title

# Shoob API integration
try:
    from shoob_api_importer import get_random_shoob_card_for_spawn
    SHOOB_API_ENABLED = True
    print("✅  Shoob API enabled!")
except Exception as e:
    SHOOB_API_ENABLED = False
    print(f"⚠️  Shoob API disabled - using local cards only")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)
db  = Database()
active_spawns = {}

COGS = [
    "cogs.cards",
    "cogs.deck_render",
    "cogs.economy",
    "cogs.games",
    "cogs.pokemon",
    "cogs.media",
    "cogs.profile",
    "cogs.utils",
    "cogs.moderation",
    "cogs.admin",
]

# ── Miku Status Messages ─────────────────────────────────────────────────────────
MIKU_STATUSES = [
    ("🎤 Singing on stage~!", discord.ActivityType.playing),
    ("🎵 Miku Miku ni Shite Ageru♪", discord.ActivityType.listening),
    ("🎴 Spawning cards for you~", discord.ActivityType.playing),
    ("💚 .help to get started~!", discord.ActivityType.watching),
    ("🌟 Collecting cards with you~", discord.ActivityType.playing),
    ("🎶 World is Mine~ ♪", discord.ActivityType.listening),
    ("⚡ Catching Pokémon~!", discord.ActivityType.playing),
    ("💫 Earning Stellas together~", discord.ActivityType.playing),
    ("🎤 Virtual idol on duty~!", discord.ActivityType.watching),
    ("🌸 Say hi to Miku~!", discord.ActivityType.playing),
]

# ── Rarity Prices ───────────────────────────────────────────────────────────────
RARITY_PRICES = {
    'Common': 1000,
    'Uncommon': 2000,
    'Rare': 5000,
    'Epic': 10000,
    'Legendary': 25000,
    'Mythic': 50000
}

# ── Events ──────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"{'='*50}")
    print(f"🎤  {bot.user} is online!")
    print(f"🌐  Connected to {len(bot.guilds)} guilds")
    print(f"{'='*50}")
    auto_spawn_cards.start()
    rotate_status.start()

@bot.before_invoke
async def before_command_invoke(ctx):
    """Handle cooldowns, XP, and level-ups before command execution"""
    # Apply cooldown to every command
    
    # Check cooldown
    cooldown_remaining = db.get_cooldown(ctx.author.id, ctx.command.name)
    if cooldown_remaining > 0:
        await ctx.send(f"⏱️ This command is on cooldown! Try again in {cooldown_remaining}s")
        raise commands.CommandError("Command on cooldown")
    
    # Set cooldown (configurable per command type)
    cooldown_seconds = 15  # Default
    
    # Admin/special commands with longer cooldown
    if ctx.command.name in ['spawn', 'claim', 'addcard', 'removecard', 'editcard', 'ban', 'mute', 'kick']:
        cooldown_seconds = 30
    
    # Card viewing/collection commands with longer cooldown
    if ctx.command.name in ['cards', 'collection', 'deck', 'findcard']:
        cooldown_seconds = 20
    
    # Economy commands
    if ctx.command.name in ['balance', 'daily', 'work', 'beg', 'rob', 'trade']:
        cooldown_seconds = 10
    
    db.set_cooldown(ctx.author.id, ctx.command.name, cooldown_seconds)
    
    # Add XP (default 10 XP per command)
    xp_reward = 10
    if ctx.command.name in ['cards', 'collection', 'deck', 'findcard']:
        xp_reward = 15
    elif ctx.command.name in ['spawn', 'claim', 'battle']:
        xp_reward = 20
    
    level_up_info = db.add_xp(ctx.author.id, xp_reward)
    
    # Store for later use (we'll handle it in after_invoke if needed)
    ctx.level_up_info = level_up_info

@bot.after_invoke
async def after_command_invoke(ctx):
    """Handle post-command notifications like level-ups"""
    if not hasattr(ctx, 'level_up_info'):
        return
    
    level_up_info = ctx.level_up_info
    if level_up_info.get('level_up'):
        new_level = level_up_info['new_level']
        reward = level_up_info['reward']
        title = get_rank_title(new_level)
        level_embed = discord.Embed(
            title="🎉 LEVEL UP!",
            description=f"{ctx.author.mention} reached **Level {new_level}** {title}",
            color=discord.Color.gold()
        )
        level_embed.add_field(name="🎁 Reward", value=f"{reward} Stellas", inline=False)
        try:
            await ctx.send(embed=level_embed)
        except:
            pass  # In case channel is deleted or bot no longer has permission

@tasks.loop(minutes=5)
async def rotate_status():
    """Rotate Miku's status every 5 minutes"""
    import random
    text, activity_type = random.choice(MIKU_STATUSES)
    activity = discord.Activity(type=activity_type, name=text)
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    is_mentioned    = bot.user in message.mentions
    is_reply_to_bot = (
        message.reference is not None and
        message.reference.resolved is not None and
        hasattr(message.reference.resolved, 'author') and
        message.reference.resolved.author == bot.user
    )
    if is_mentioned or is_reply_to_bot:
        if message.content.startswith('.'):
            await bot.process_commands(message)
            return
        user_msg = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        if not user_msg:
            user_msg = "Hello!"
        async with message.channel.typing():
            stellas = db.get_user_stellas(message.author.id)
            stats   = db.get_user_stats(message.author.id)
            context = (
                f"{message.author.display_name} has {stellas} Stellas, "
                f"{stats['total_cards']} cards, {stats['unique_cards']} unique. "
                f"Collection {stats['completion_percentage']:.1f}% complete."
            )
            response = await get_ai_response(user_msg, message.author.display_name, context)
        await message.reply(response)
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument! Use `.help {ctx.command}` for usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument! Check the command usage.")

# ── Auto Spawn ───────────────────────────────────────────────────────────────────
@tasks.loop(minutes=15)
async def auto_spawn_cards():
    for guild in bot.guilds:
        # Check if spawn channel is configured
        spawn_channel_id = db.get_config('spawn_channel')
        if spawn_channel_id:
            channel = bot.get_channel(int(spawn_channel_id))
            if channel and channel.permissions_for(guild.me).send_messages:
                await spawn_card(channel)
        else:
            # Random channel if not configured
            channels = [ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages]
            if channels:
                await spawn_card(random.choice(channels))

@auto_spawn_cards.before_loop
async def before_spawn():
    await bot.wait_until_ready()

@rotate_status.before_loop
async def before_status():
    await bot.wait_until_ready()

async def spawn_card(channel):
    # Try Shoob API first, fallback to local database
    if SHOOB_API_ENABLED:
        try:
            card = get_random_shoob_card_for_spawn()
        except Exception:
            card = db.get_random_card()
    else:
        card = db.get_random_card()
    
    if not card:
        return

    # Generate random 4-character captcha
    import string
    captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    miku_msg = await get_spawn_message(card['name'], card['rarity'])

    # Card embed with all details
    embed = discord.Embed(
        title=f"🎴 {card['name']}",
        description=f"**{card['series']}**\n\n*{miku_msg}*",
        color=get_rarity_color(card['rarity'])
    )
    
    embed.set_image(url=card['image_url'])
    embed.add_field(name="🔐 Captcha", value=f"`{captcha}`", inline=False)
    embed.set_footer(text="Type .claim <captcha> to claim this card! First correct claim wins.")

    # Ping everyone
    message = await channel.send("@everyone", embed=embed)
    
    # Clear old spawn in this channel
    if channel.id in active_spawns:
        old_spawn = active_spawns[channel.id]
        if not old_spawn['claimed']:
            try:
                old_message = await channel.fetch_message(old_spawn['message_id'])
                old_embed = old_message.embeds[0]
                old_embed.set_footer(text="❌ Expired! New card spawned.")
                await old_message.edit(embed=old_embed)
            except:
                pass
    
    active_spawns[channel.id] = {
        'card': card,
        'captcha': captcha,
        'message_id': message.id,
        'claimed': False,
        'spawn_time': datetime.now()
    }


def get_rarity_color(rarity):
    return {'Common': discord.Color.light_grey(), 'Uncommon': discord.Color.green(),
            'Rare': discord.Color.blue(), 'Epic': discord.Color.purple(),
            'Legendary': discord.Color.gold(), 'Mythic': discord.Color.red()
            }.get(rarity, discord.Color.default())

# ── Claim Command ───────────────────────────────────────────────────────────────
@bot.command(name="claim")
async def claim_card(ctx, captcha: str = None):
    """Claim a spawned card with captcha"""
    if ctx.channel.id not in active_spawns:
        await ctx.send("❌ No card spawned yet! Wait for Miku to drop one~")
        return
    
    spawn = active_spawns[ctx.channel.id]
    
    if spawn['claimed']:
        await ctx.send(f"💨 Sorry {ctx.author.mention}, someone already claimed this card~!")
        return
    
    if not captcha:
        await ctx.send(f"❌ Use `.claim <captcha>` to claim this card! Check the card embed for the code~")
        return
    
    if captcha.upper() != spawn['captcha'].upper():
        await ctx.send(f"❌ Invalid captcha, {ctx.author.mention}! Try again~")
        return
    
    # Mark as claimed
    spawn['claimed'] = True
    card = spawn['card']
    
    # Add to user's collection
    db.add_card_to_user(ctx.author.id, card['id'])
    
    # Update embed
    try:
        channel = bot.get_channel(ctx.channel.id)
        message = await channel.fetch_message(spawn['message_id'])
        embed = message.embeds[0]
        embed.color = discord.Color.green()
        embed.set_footer(text=f"🎉 Claimed by {ctx.author.display_name}!")
        await message.edit(embed=embed)
    except:
        pass
    
    # Miku's congratulations
    claim_msg = await get_claim_message(card['name'], card['rarity'], ctx.author.display_name)
    await ctx.send(f"🎉 {ctx.author.mention} {claim_msg}")
    
    # Clear spawn
    del active_spawns[ctx.channel.id]

# ── Settings Commands ────────────────────────────────────────────────────────────
@bot.command(name="setchannel")
@commands.has_permissions(administrator=True)
async def set_spawn_channel(ctx, channel: discord.TextChannel = None):
    """Set the channel where cards spawn"""
    channel = channel or ctx.channel
    db.set_config('spawn_channel', str(channel.id))
    await ctx.send(f"✅ Cards will now spawn in {channel.mention}!")

@bot.command(name="pingall", aliases=["massping"])
@commands.has_permissions(administrator=True)
async def ping_all(ctx):
    """Ping all server members"""
    await ctx.send(f"@everyone 🎤 Miku says hello to everyone~!")

# ── Welcome System ───────────────────────────────────────────────────────────────
@bot.event
async def on_member_join(member):
    """Welcome new members"""
    # Try to find a welcome channel
    welcome_channel_id = db.get_config('welcome_channel')
    if welcome_channel_id:
        channel = bot.get_channel(int(welcome_channel_id))
    else:
        # Default to first text channel bot can write in
        channel = next((ch for ch in member.guild.text_channels if ch.permissions_for(member.guild.me).send_messages), None)
    
    if not channel:
        return
    
    embed = discord.Embed(
        title=f"🎤 Welcome to {member.guild.name}!",
        description=f"Hey {member.mention}~! Miku is so happy you're here! 💚",
        color=discord.Color.from_rgb(0, 210, 180)
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="📝 Get Started", value="Type `.help` to see all my commands!", inline=False)
    embed.add_field(name="🎴 Collect Cards", value="Cards spawn every 15 minutes! Use `.claim <captcha>` to grab them!", inline=False)
    embed.set_footer(text=f"Member #{member.guild.member_count}")
    
    await channel.send(f"@everyone", embed=embed)

@bot.command(name="setwelcome")
@commands.has_permissions(administrator=True)
async def set_welcome_channel(ctx, channel: discord.TextChannel = None):
    """Set the channel for welcome messages"""
    channel = channel or ctx.channel
    db.set_config('welcome_channel', str(channel.id))
    await ctx.send(f"✅ New members will be welcomed in {channel.mention}!")

# ── Help ─────────────────────────────────────────────────────────────────────────
@bot.command(name="help", aliases=["h", "commands"])
async def help_command(ctx, category: str = None):
    P = "."
    CATS = {
        "cards":      ("🎴", "Card collecting, trading & market",
                       [(".claim <captcha>","Claim a spawned card"), (".collection","View your card collection"),
                        (".cards","Browse all cards"), (".card <id>","View a card"),
                        (".deck","View your deck image"), (".decklist","View deck as text"),
                        (".t2d <collection_index>","Move card to deck"),
                        (".t2c <deck_position>","Move card back"), (".all2coll","Clear your deck"),
                        (".dupes","Duplicate cards"),
                        (".findcard <n>","Search cards"), (".cardgive @u <id>","Give a card"),
                        (".merge <id>","Merge duplicates"), (".wishlist add <id>","Save wanted cards"),
                        (".fav <id>","Feature a favorite card"), (".recent","Recent collected cards"),
                        (".cardstats","Card database stats"), (".checkcard <id>","Check card details")]),
        "economy":    ("💫", "Stellas currency & economy",
                       [(".daily","Claim daily Stellas"), (".weekly","Weekly bonus"),
                        (".balance","Your Stellas balance"), (".leaderboard","Top players"),
                        (".give @u <amt>","Give Stellas"),
                        (".rob @user","Rob someone"), (".dice <amt>","Dice bet"),
                        (".slot <amt>","Slot machine"), (".roulette <amt>","Roulette"),
                        (".store","Item store"), (".buy <item>","Buy item"),
                        (".items","Your items"), (".gems","Your gems"),
                        (".shards","Your shards"), (".convert","Convert currency"),
                        (".roll","Random card pack (100⭐)")]),
        "games":      ("🎮", "Fun games to play",
                       [(".quiz","Start a quiz"), (".answer <ans>","Answer quiz"),
                        (".hangman","Play hangman"), (".chess @user","Challenge to chess"),
                        (".accept","Accept challenge"), (".reject","Reject challenge"),
                        (".forfeit","Forfeit game")]),
        "pokemon":    ("⚡", "Catch & battle Pokémon",
                       [(".startjourney","Begin journey"), (".catch","Catch wild Pokémon"),
                        (".pokemon","Your Pokémon"), (".pokedex","Browse Pokédex"),
                        (".findpoke <n>","Find Pokémon"), (".party","Battle party"),
                        (".pc","PC storage"), (".battle @user","Battle trainer"),
                        (".heal","Heal Pokémon"), (".learn <move>","Teach move"),
                        (".swap <id>","Swap party Pokémon")]),
        "media":      ("🎵", "Music, social media & downloads",
                       [(".lyrics <song>","Song lyrics"), (".song <name>","Search song"),
                        (".artist <n>","Artist info & top tracks"), (".album <n>","Album info"),
                        (".yts <q>","YouTube song"), (".tiktok <url>","Download TikTok"),
                        (".igdl <url>","Download Instagram"), (".facebook <url>","Download Facebook"),
                        (".x <url>","Download X/Twitter"), (".pinterest <q>","Search Pinterest"),
                        (".x <url>","Download X/Twitter"), (".pinterest <q>","Search Pinterest")]),
        "profile":    ("👤", "Customize your profile",
                       [(".profile","View your profile"), (".setbio <text>","Set bio"),
                        (".seticon <url>","Set profile icon"), (".setusername <n>","Set username"),
                        (".resetbio","Reset bio"), (".reseticon","Reset icon"),
                        (".resetusername","Reset username"), (".lockprofile","Lock profile"),
                        (".unlockprofile","Unlock profile"), (".rank","Your rank"),
                        (".exp","Your XP progress")]),
        "utils":      ("🔧", "Useful utility tools",
                       [(".ai <text>","Chat with Miku AI"), (".translate <txt>","Translate text"),
                        (".weather <city>","Weather info"), (".define <word>","Dictionary"),
                        (".urbandic <word>","Urban Dictionary"), (".horoscope <sign>","Horoscope"),
                        (".bible <verse>","Bible verse"), (".quran <verse>","Quran verse"),
                        (".emoji <name>","Emoji info"), (".emojimix <e1+e2>","Mix emojis"),
                        (".sticker <url>","Make sticker"), (".toimage","Sticker to image"),
                        (".upload <url>","Upload file")]),
        "moderation": ("🛡️", "Server moderation",
                       [(".ban @user","Ban member"), (".kick @user","Kick member"),
                        (".mute @user","Mute member"), (".unmute @user","Unmute member"),
                        (".warn @user","Warn member"), (".promote @user","Promote member"),
                        (".demote @user","Demote member"), (".ping","Bot latency"),
                        (".open","Open channel"), (".close","Close channel"),
                        (".enable <cmd>","Enable command"), (".disable <cmd>","Disable command")]),
        "admin":      ("👑", "Admin & owner commands",
                       [(".addcard","Create a card"), (".editcard","Edit a card"),
                        (".removecard","Delete a card"), (".listcards","View all cards"),
                        (".addstellas @u <amt>","Give Stellas"), (".setdaily <amt>","Set daily reward"),
                        (".spawn","Manually spawn card"), (".givepoke @u","Give Pokémon"),
                        (".addgems @u <amt>","Give gems"), (".resetuser @u","Reset user data"), 
                        (".setweekly <amt>","Set weekly reward"), (".botstats","View bot stats")])
    }

    if category is None:
        embed = discord.Embed(
            title="🎤  Miku's Card Bot — Command Menu",
            description=(
                "**Built for speed. Designed for power.**\n"
                f"Use `{P}help <category>` for detailed commands\n"
                "──────────────────────────────"
            ),
            color=discord.Color.from_rgb(0, 210, 180)
        )
        for key, (emoji, desc, cmds) in CATS.items():
            preview = " · ".join(f"`{c[0]}`" for c in cmds[:4])
            embed.add_field(
                name=f"{emoji}  {key.capitalize()}",
                value=f"{desc}\n{preview}...\n`{P}help {key}`",
                inline=True
            )
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(
            name="💡  Quick Tips",
            value=(
                f"• Tag me or reply to chat with Miku~!\n"
                f"• Cards auto-spawn every **15 minutes**\n"
                f"• `{P}daily` every 24h for free Stellas\n"
                f"• `{P}help <category>` for full command list"
            ),
            inline=False
        )
        embed.set_footer(text="✨  Miku's Card Bot  •  .help <category> for details")
        await ctx.send(embed=embed)
        return

    cat_data = CATS.get(category.lower())
    if not cat_data:
        await ctx.send(f"❌ Unknown category `{category}`! Options: {', '.join(CATS.keys())}")
        return

    emoji, desc, cmds = cat_data
    embed = discord.Embed(
        title=f"{emoji}  {category.capitalize()} Commands",
        description=f"{desc}\n──────────────────────────────",
        color=discord.Color.from_rgb(0, 210, 180)
    )
    for cmd, cdesc in cmds:
        embed.add_field(name=f"`{cmd}`", value=cdesc, inline=True)
    embed.set_footer(text=f"{P}help for all categories")
    await ctx.send(embed=embed)

# ── Entry point ──────────────────────────────────────────────────────────────────
async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"  ✅  Loaded {cog}")
            except Exception as e:
                print(f"  ❌  Failed {cog}: {e}")
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
