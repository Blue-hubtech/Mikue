import discord
from discord.ext import commands
from database import Database
import random

db = Database()

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="balance", aliases=["bal", "wallet", "stellas"])
    async def balance(self, ctx, user: discord.User = None):
        target  = user or ctx.author
        stellas = db.get_user_stellas(target.id)
        embed   = discord.Embed(title=f"💫 {target.display_name}'s Balance", description=f"**{stellas:,}** Stellas ⭐", color=discord.Color.gold())
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard(self, ctx, category: str = "stellas"):
        """Show top players by stellas, cards, unique cards, or XP"""
        aliases = {
            "money": "stellas",
            "bal": "stellas",
            "balance": "stellas",
            "card": "cards",
            "collection": "cards",
            "uniques": "unique",
            "levels": "xp",
            "level": "xp",
        }
        category = aliases.get(category.lower(), category.lower())
        if category not in ["stellas", "cards", "unique", "xp"]:
            await ctx.send("Use `.lb stellas`, `.lb cards`, `.lb unique`, or `.lb xp`.")
            return

        rows = db.get_leaderboard(category, 10)
        if not rows:
            await ctx.send("No leaderboard data yet. Use some commands and collect cards first!")
            return

        labels = {
            "stellas": "Stellas",
            "cards": "Total Cards",
            "unique": "Unique Cards",
            "xp": "XP"
        }
        lines = []
        for index, row in enumerate(rows, start=1):
            member = ctx.guild.get_member(row['user_id']) if ctx.guild else None
            name = member.display_name if member else f"User {row['user_id']}"
            lines.append(f"`#{index}` **{name}** - {row['score']:,}")

        embed = discord.Embed(
            title=f"Top {labels[category]}",
            description="\n".join(lines),
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @commands.command(name="daily")
    async def daily(self, ctx):
        success, amount, hours = db.claim_daily(ctx.author.id)
        if success:
            embed = discord.Embed(title="🎁 Daily Reward!", description=f"You got **{amount:,}** Stellas! 💫", color=discord.Color.green())
            embed.set_footer(text="Come back in 24 hours~!")
        else:
            embed = discord.Embed(title="⏰ Not Ready!", description=f"Next daily in **{hours:.1f}h**", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(name="weekly")
    async def weekly(self, ctx):
        success, amount, hours = db.claim_weekly(ctx.author.id)
        if success:
            embed = discord.Embed(title="🎉 Weekly Reward!", description=f"You got **{amount:,}** Stellas! 💫", color=discord.Color.green())
        else:
            embed = discord.Embed(title="⏰ Not Ready!", description=f"Next weekly in **{hours:.1f}h**", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(name="give", aliases=["transfer", "pay"])
    async def give(self, ctx, user: discord.User, amount: int):
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        if user.id == ctx.author.id:
            await ctx.send("❌ You can't give to yourself!")
            return
        if db.transfer_stellas(ctx.author.id, user.id, amount):
            embed = discord.Embed(title="💸 Transfer!", description=f"{ctx.author.mention} → {user.mention}\n**{amount:,}** Stellas", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Not enough Stellas! Need **{amount:,}**")

    @commands.command(name="rob")
    async def rob(self, ctx, user: discord.User):
        if user.id == ctx.author.id:
            await ctx.send("❌ Can't rob yourself lol")
            return
        victim_stellas = db.get_user_stellas(user.id)
        if victim_stellas < 100:
            await ctx.send(f"❌ {user.display_name} is too broke to rob!")
            return
        success = random.random() < 0.4  # 40% success rate
        if success:
            stolen = random.randint(50, min(500, victim_stellas // 4))
            db.transfer_stellas(user.id, ctx.author.id, stolen)
            embed = discord.Embed(title="🦹 Robbery Successful!", description=f"You stole **{stolen:,}** Stellas from {user.mention}!", color=discord.Color.green())
        else:
            fine = random.randint(50, 200)
            db.transfer_stellas(ctx.author.id, user.id, min(fine, db.get_user_stellas(ctx.author.id)))
            embed = discord.Embed(title="🚔 Caught!", description=f"You got caught and paid **{fine:,}** Stellas as a fine!", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(name="dice")
    async def dice(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("❌ Bet must be positive!")
            return
        if db.get_user_stellas(ctx.author.id) < amount:
            await ctx.send("❌ Not enough Stellas!")
            return
        your_roll = random.randint(1, 6)
        bot_roll  = random.randint(1, 6)
        if your_roll > bot_roll:
            db.add_stellas(ctx.author.id, amount)
            result = f"🎉 You won **{amount:,}** Stellas!"
            color  = discord.Color.green()
        elif your_roll < bot_roll:
            db.remove_stellas(ctx.author.id, amount)
            result = f"💀 You lost **{amount:,}** Stellas!"
            color  = discord.Color.red()
        else:
            result = "🤝 It's a tie! No Stellas lost."
            color  = discord.Color.yellow()
        embed = discord.Embed(title="🎲 Dice Roll!", color=color)
        embed.add_field(name="Your Roll", value=f"🎲 {your_roll}", inline=True)
        embed.add_field(name="Bot Roll",  value=f"🎲 {bot_roll}",  inline=True)
        embed.add_field(name="Result",    value=result,             inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="slot")
    async def slot(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("❌ Bet must be positive!")
            return
        if db.get_user_stellas(ctx.author.id) < amount:
            await ctx.send("❌ Not enough Stellas!")
            return
        symbols = ["🍒","🍋","🍇","⭐","💎","🎰"]
        reels   = [random.choice(symbols) for _ in range(3)]
        if reels[0] == reels[1] == reels[2]:
            if reels[0] == "💎":
                mult = 10
            elif reels[0] == "⭐":
                mult = 5
            else:
                mult = 3
            winnings = amount * mult
            db.add_stellas(ctx.author.id, winnings)
            result = f"🎉 JACKPOT! ×{mult} — Won **{winnings:,}** Stellas!"
            color  = discord.Color.gold()
        elif reels[0] == reels[1] or reels[1] == reels[2]:
            db.add_stellas(ctx.author.id, amount // 2)
            result = f"😊 Partial match! Got back **{amount//2:,}** Stellas"
            color  = discord.Color.yellow()
        else:
            db.remove_stellas(ctx.author.id, amount)
            result = f"💀 No match. Lost **{amount:,}** Stellas"
            color  = discord.Color.red()
        embed = discord.Embed(title="🎰 Slot Machine!", description=f"{'  '.join(reels)}\n\n{result}", color=color)
        await ctx.send(embed=embed)

    @commands.command(name="roulette")
    async def roulette(self, ctx, amount: int, choice: str = "red"):
        if amount <= 0:
            await ctx.send("❌ Bet must be positive!")
            return
        if db.get_user_stellas(ctx.author.id) < amount:
            await ctx.send("❌ Not enough Stellas!")
            return
        valid = ["red","black","green","odd","even"]
        choice = choice.lower()
        if choice not in valid:
            await ctx.send(f"❌ Choose from: {', '.join(valid)}")
            return
        number   = random.randint(0, 36)
        is_red   = number in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
        is_green = number == 0
        is_black = not is_red and not is_green
        won = False
        mult = 2
        if choice == "red"   and is_red:   won = True
        if choice == "black" and is_black: won = True
        if choice == "green" and is_green: won, mult = True, 14
        if choice == "odd"   and number % 2 == 1 and number != 0: won = True
        if choice == "even"  and number % 2 == 0 and number != 0: won = True
        color_emoji = "🔴" if is_red else ("⬛" if is_black else "🟢")
        if won:
            winnings = amount * mult
            db.add_stellas(ctx.author.id, winnings)
            result = f"🎉 Won **{winnings:,}** Stellas!"
            color  = discord.Color.green()
        else:
            db.remove_stellas(ctx.author.id, amount)
            result = f"💀 Lost **{amount:,}** Stellas!"
            color  = discord.Color.red()
        embed = discord.Embed(title="🎡 Roulette!", description=f"{color_emoji} **{number}**\n\n{result}", color=color)
        await ctx.send(embed=embed)

    @commands.command(name="roll")
    async def roll(self, ctx):
        cost = 100
        if not db.remove_stellas(ctx.author.id, cost):
            await ctx.send(f"❌ Need **{cost}** Stellas to roll!")
            return
        card = db.get_random_card()
        if not card:
            await ctx.send("❌ No cards in database!")
            return
        db.add_card_to_user(ctx.author.id, card['id'])
        embed = discord.Embed(title="🎲 Card Roll!", description=f"You rolled **{card['name']}**!", color=discord.Color.purple())
        embed.add_field(name="Rarity", value=card['rarity'], inline=True)
        embed.add_field(name="Series", value=card['series'], inline=True)
        embed.set_image(url=card['image_url'])
        await ctx.send(embed=embed)

    @commands.command(name="store")
    async def store(self, ctx):
        embed = discord.Embed(title="🏪 Item Store", description="Spend your Stellas!", color=discord.Color.blue())
        items = [("🎴 Card Pack","100 ⭐","A random card"), ("💎 Gem Pack","500 ⭐","10 gems"), ("⚡ Pokéball","200 ⭐","Catch Pokémon"), ("🛡️ Shield","300 ⭐","Rob protection")]
        for name, price, desc in items:
            embed.add_field(name=name, value=f"{price}\n{desc}", inline=True)
        embed.set_footer(text=".buy <item> to purchase")
        await ctx.send(embed=embed)

    @commands.command(name="buy")
    async def buy(self, ctx, *, item: str):
        prices = {"card pack": 100, "gem pack": 500, "pokeball": 200, "shield": 300}
        item_lower = item.lower()
        price = prices.get(item_lower)
        if not price:
            await ctx.send(f"❌ Item not found! Use `.store` to browse.")
            return
        if not db.remove_stellas(ctx.author.id, price):
            await ctx.send(f"❌ Not enough Stellas! Need **{price:,}**")
            return
        if item_lower == "card pack":
            card = db.get_random_card()
            if card:
                db.add_card_to_user(ctx.author.id, card['id'])
                await ctx.send(f"✅ Bought Card Pack! Got **{card['name']}** ({card['rarity']})!")
        else:
            await ctx.send(f"✅ Bought **{item}** for **{price:,}** Stellas!")

    @commands.command(name="items")
    async def items(self, ctx):
        await ctx.send("🎒 Inventory system coming soon~! 🎤💚")

    @commands.command(name="gems")
    async def gems(self, ctx):
        gems = db.get_user_gems(ctx.author.id)
        await ctx.send(f"💎 You have **{gems}** gems!")

    @commands.command(name="shards")
    async def shards(self, ctx):
        await ctx.send("🔮 Shard system coming soon~! 🎤💚")

    @commands.command(name="convert")
    async def convert(self, ctx, amount: int, from_cur: str = "gems", to_cur: str = "stellas"):
        await ctx.send("🔄 Currency conversion coming soon~! 🎤💚")

async def setup(bot):
    await bot.add_cog(Economy(bot))
