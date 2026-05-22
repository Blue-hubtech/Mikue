import discord
from discord.ext import commands
from database import Database
import asyncio

db = Database()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addcard", aliases=["createcard"])
    @commands.has_permissions(administrator=True)
    async def addcard(self, ctx, rarity: str, series: str, *, name: str):
        valid = ['Common','Uncommon','Rare','Epic','Legendary','Mythic']
        rarity = rarity.capitalize()
        if rarity not in valid:
            await ctx.send(f"❌ Rarity must be: {', '.join(valid)}")
            return
        await ctx.send(f"📸 Send image URL or attach image for **{name}** ({rarity})!\nType 'cancel' to abort.")
        def check(m): return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            if msg.content.lower() == 'cancel':
                await ctx.send("❌ Cancelled!")
                return
            image_url = msg.attachments[0].url if msg.attachments else msg.content.strip()
            if not image_url.startswith('http'):
                await ctx.send("❌ Invalid URL!")
                return
            card_id = db.add_custom_card(name, series, rarity, image_url)
            embed = discord.Embed(title="✅ Card Created!", description=f"**{name}** added!", color=discord.Color.green())
            embed.add_field(name="ID",     value=f"#{card_id}", inline=True)
            embed.add_field(name="Series", value=series,        inline=True)
            embed.add_field(name="Rarity", value=rarity,        inline=True)
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("❌ Timed out!")

    @commands.command(name="editcard", aliases=["updatecard"])
    @commands.has_permissions(administrator=True)
    async def editcard(self, ctx, card_id: int, field: str, *, value: str):
        card = db.get_card_by_id(card_id)
        if not card:
            await ctx.send(f"❌ Card #{card_id} not found!")
            return
        field = field.lower()
        cols  = {'name':'name','series':'series','rarity':'rarity','image':'image_url','image_url':'image_url'}
        if field not in cols:
            await ctx.send("❌ Field must be: name, series, rarity, image")
            return
        if field == 'rarity':
            value = value.capitalize()
            if value not in ['Common','Uncommon','Rare','Epic','Legendary','Mythic']:
                await ctx.send("❌ Invalid rarity!")
                return
        conn = db.get_connection(); cursor = conn.cursor()
        cursor.execute(f"UPDATE cards SET {cols[field]}=? WHERE id=?", (value, card_id))
        conn.commit(); conn.close()
        await ctx.send(f"✅ Card #{card_id} {field} → **{value}**")

    @commands.command(name="removecard", aliases=["deletecard"])
    @commands.has_permissions(administrator=True)
    async def removecard(self, ctx, card_id: int):
        card = db.get_card_by_id(card_id)
        if not card:
            await ctx.send(f"❌ Card #{card_id} not found!")
            return
        await ctx.send(f"⚠️ Delete **{card['name']}** (#{card_id})? Type `yes` or `no`")
        def check(m): return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes','no']
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
            if msg.content.lower() == 'yes':
                conn = db.get_connection(); cursor = conn.cursor()
                cursor.execute("DELETE FROM cards WHERE id=?", (card_id,))
                conn.commit(); conn.close()
                await ctx.send(f"✅ Deleted **{card['name']}**!")
            else:
                await ctx.send("❌ Cancelled!")
        except Exception:
            await ctx.send("❌ Timed out!")

    @commands.command(name="listcards", aliases=["allcards"])
    @commands.has_permissions(administrator=True)
    async def listcards(self, ctx, page: int = 1):
        conn = db.get_connection(); cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as c FROM cards")
        total = cursor.fetchone()['c']
        per   = 10
        total_pages = max(1, (total + per - 1) // per)
        page  = max(1, min(page, total_pages))
        cursor.execute("SELECT id,name,series,rarity FROM cards ORDER BY id LIMIT ? OFFSET ?", (per, (page-1)*per))
        rows  = [dict(r) for r in cursor.fetchall()]
        conn.close()
        embed = discord.Embed(title=f"📋 Card Database ({page}/{total_pages})", description=f"Total: {total}", color=discord.Color.blue())
        for r in rows:
            embed.add_field(name=f"#{r['id']} {r['name']}", value=f"{r['series']} · {r['rarity']}", inline=False)
        embed.set_footer(text=f".listcards {page+1} for next" if page < total_pages else "Last page")
        await ctx.send(embed=embed)

    @commands.command(name="addstellas")
    @commands.has_permissions(administrator=True)
    async def addstellas(self, ctx, user: discord.User, amount: int):
        db.add_stellas(user.id, amount)
        await ctx.send(f"✅ Added **{amount:,}** Stellas to {user.mention}!")

    @commands.command(name="addgems")
    @commands.has_permissions(administrator=True)
    async def addgems(self, ctx, user: discord.User, amount: int):
        db.add_gems(user.id, amount)
        await ctx.send(f"✅ Added **{amount}** gems to {user.mention}!")

    @commands.command(name="setdaily")
    @commands.has_permissions(administrator=True)
    async def setdaily(self, ctx, amount: int):
        db.set_config('daily_min', amount)
        db.set_config('daily_max', amount)
        await ctx.send(f"✅ Daily reward set to **{amount}** Stellas!")

    @commands.command(name="setweekly")
    @commands.has_permissions(administrator=True)
    async def setweekly(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("Weekly reward must be positive.")
            return
        db.set_config('weekly_min', amount)
        db.set_config('weekly_max', amount)
        await ctx.send(f"Weekly reward set to **{amount:,}** Stellas!")

    @commands.command(name="botstats")
    @commands.has_permissions(administrator=True)
    async def botstats(self, ctx):
        stats = db.get_card_stats()
        embed = discord.Embed(title="Miku Bot Stats", color=discord.Color.from_rgb(0, 210, 180))
        embed.add_field(name="Guilds", value=f"{len(self.bot.guilds):,}", inline=True)
        embed.add_field(name="Cards", value=f"{stats['total_cards']:,}", inline=True)
        embed.add_field(name="Collected", value=f"{stats['claimed_cards']:,}", inline=True)
        embed.add_field(name="Collectors", value=f"{stats['collectors']:,}", inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="spawn")
    @commands.has_permissions(administrator=True)
    async def spawn(self, ctx):
        from bot import spawn_card
        await ctx.send("🎴 Spawning a card...")
        await spawn_card(ctx.channel)

    @commands.command(name="givepoke")
    @commands.has_permissions(administrator=True)
    async def givepoke(self, ctx, user: discord.User, *, name: str):
        from cogs.pokemon import POKEMON_LIST
        poke = next((p for p in POKEMON_LIST if p['name'].lower() == name.lower()), None)
        if not poke:
            await ctx.send(f"❌ Pokémon **{name}** not found!")
            return
        db.add_pokemon_to_user(user.id, poke['name'], poke)
        await ctx.send(f"✅ Gave **{poke['emoji']} {poke['name']}** to {user.mention}!")

    @commands.command(name="resetuser")
    @commands.has_permissions(administrator=True)
    async def resetuser(self, ctx, user: discord.User):
        await ctx.send(f"⚠️ Reset ALL data for {user.mention}? Type `yes` or `no`")
        def check(m): return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes','no']
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
            if msg.content.lower() == 'yes':
                conn = db.get_connection(); cursor = conn.cursor()
                cursor.execute("DELETE FROM user_cards WHERE user_id=?", (user.id,))
                cursor.execute("DELETE FROM users WHERE user_id=?", (user.id,))
                cursor.execute("DELETE FROM user_pokemon WHERE user_id=?", (user.id,))
                cursor.execute("DELETE FROM profiles WHERE user_id=?", (user.id,))
                conn.commit(); conn.close()
                await ctx.send(f"✅ Reset all data for {user.mention}!")
            else:
                await ctx.send("❌ Cancelled!")
        except Exception:
            await ctx.send("❌ Timed out!")


async def setup(bot):
    await bot.add_cog(Admin(bot))
