import discord
from discord.ext import commands
from database import Database

db = Database()

class Cards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── COLLECTION ──────────────────────────────────────────────────────────────
    @commands.command(name="collection", aliases=["col", "coll"])
    async def collection(self, ctx, user: discord.User = None, page: int = 1):
        target = user or ctx.author
        cards = db.get_user_collection(target.id)
        if not cards:
            await ctx.send(f"{'You have' if target == ctx.author else f'{target.display_name} has'} no cards yet!")
            return
        per_page = 10
        total_pages = max(1, (len(cards) + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        start = (page - 1) * per_page
        end = start + per_page
        embed = discord.Embed(title=f"📚 {target.display_name}'s Collection", description=f"**{len(cards)}** unique cards | Page {page}/{total_pages}", color=discord.Color.blue())
        for idx, card in enumerate(cards[start:end], start + 1):
            embed.add_field(name=f"{idx}. {card['name']}", value=f"{card['series']} • {card['rarity']} ×{card['count']}", inline=True)
        embed.set_footer(text=f"Use .collection {page+1} for next page" if page < total_pages else "Last page")
        await ctx.send(embed=embed)

    # ── TRANSFER TO DECK (t2d) ───────────────────────────────────────────────────
    @commands.command(name="t2d", aliases=["transfertodeck"])
    async def transfer_to_deck(self, ctx, collection_index: int):
        """Move a card from collection to deck (removes from collection)"""
        cards = db.get_user_collection(ctx.author.id)
        if not cards or collection_index < 1 or collection_index > len(cards):
            await ctx.send(f"❌ Invalid collection index! You have {len(cards) if cards else 0} unique cards.")
            return
        
        card = cards[collection_index - 1]
        success, msg = db.add_to_deck(ctx.author.id, card['id'])
        
        if success:
            await ctx.send(f"✅ {msg} – **{card['name']}** is now in your deck.")
        else:
            await ctx.send(f"❌ {msg}")

    # ── TRANSFER TO COLLECTION (t2c) ────────────────────────────────────────────
    @commands.command(name="t2c", aliases=["transfertocollection"])
    async def transfer_to_collection(self, ctx, deck_position: int):
        """Move a card from deck back to collection"""
        if db.remove_from_deck(ctx.author.id, deck_position):
            await ctx.send(f"✅ Removed card from deck position {deck_position} and returned to collection.")
        else:
            await ctx.send(f"❌ No card at position {deck_position}!")

    # ── CLEAR DECK (all2coll) ───────────────────────────────────────────────────
    @commands.command(name="all2coll", aliases=["cleardeck"])
    async def all_to_collection(self, ctx):
        """Move all deck cards back to collection"""
        count = db.transfer_all_to_collection(ctx.author.id)
        if count > 0:
            await ctx.send(f"✅ Moved **{count}** card(s) from deck to collection.")
        else:
            await ctx.send("❌ Your deck is already empty!")

    # ── VIEW DECK (visual, handled by deck_render.py) ───────────────────────────
    # The .deck command is now in cogs/deck_render.py – remove any old .deck from this file.

    # ── OTHER CARD COMMANDS (unchanged) ─────────────────────────────────────────
    @commands.command(name="card", aliases=["view", "checkcard"])
    async def card(self, ctx, card_id: int):
        card = db.get_card_by_id(card_id)
        if not card:
            await ctx.send(f"❌ Card #{card_id} not found!")
            return
        owns = db.check_user_owns_card(ctx.author.id, card_id)
        embed = discord.Embed(title=f"🎴 {card['name']}", description=card['series'], color=discord.Color.blue())
        embed.add_field(name="ID", value=f"#{card['id']}", inline=True)
        embed.add_field(name="Rarity", value=card['rarity'], inline=True)
        embed.add_field(name="You Own", value=f"×{owns}" if owns else "Not owned", inline=True)
        embed.set_image(url=card['image_url'])
        await ctx.send(embed=embed)

    @commands.command(name="cards")
    async def browse_cards(self, ctx, page: int = 1):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as c FROM cards")
        total = cursor.fetchone()['c']
        per = 12
        total_pages = max(1, (total + per - 1) // per)
        page = max(1, min(page, total_pages))
        cursor.execute("SELECT id,name,series,rarity FROM cards ORDER BY id LIMIT ? OFFSET ?", (per, (page-1)*per))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        embed = discord.Embed(title=f"🃏 All Cards (Page {page}/{total_pages})", description=f"Total: {total} cards", color=discord.Color.blue())
        for r in rows:
            embed.add_field(name=f"#{r['id']} {r['name']}", value=f"{r['series']} · {r['rarity']}", inline=True)
        embed.set_footer(text=f".cards {page+1} for next page" if page < total_pages else "Last page")
        await ctx.send(embed=embed)

    @commands.command(name="findcard", aliases=["searchcard"])
    async def findcard(self, ctx, *, query: str):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id,name,series,rarity FROM cards WHERE name LIKE ? OR series LIKE ? LIMIT 10", (f"%{query}%", f"%{query}%"))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        if not rows:
            await ctx.send(f"❌ No cards found for **{query}**")
            return
        embed = discord.Embed(title=f"🔍 Results for '{query}'", color=discord.Color.blue())
        for r in rows:
            embed.add_field(name=f"#{r['id']} {r['name']}", value=f"{r['series']} · {r['rarity']}", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="dupes")
    async def dupes(self, ctx):
        cards = db.get_user_collection(ctx.author.id)
        dupes = [c for c in cards if c['count'] > 1]
        if not dupes:
            await ctx.send("✅ No duplicate cards!")
            return
        embed = discord.Embed(title="🔄 Duplicate Cards", color=discord.Color.orange())
        for c in dupes[:10]:
            embed.add_field(name=c['name'], value=f"{c['rarity']} ×{c['count']}", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="cardgive")
    async def cardgive(self, ctx, user: discord.User, card_id: int):
        if not db.check_user_owns_card(ctx.author.id, card_id):
            await ctx.send("❌ You don't own that card!")
            return
        card = db.get_card_by_id(card_id)
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM user_cards
            WHERE id = (
                SELECT id FROM user_cards
                WHERE user_id=? AND card_id=?
                LIMIT 1
            )
            """,
            (ctx.author.id, card_id)
        )
        conn.commit()
        conn.close()
        db.add_card_to_user(user.id, card_id)
        await ctx.send(f"✅ Gave **{card['name']}** to {user.mention}!")

    @commands.command(name="merge")
    async def merge(self, ctx, card_id: int):
        owns = db.check_user_owns_card(ctx.author.id, card_id)
        if owns < 2:
            await ctx.send("❌ You need at least 2 copies to merge!")
            return
        card = db.get_card_by_id(card_id)
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM user_cards
            WHERE id = (
                SELECT id FROM user_cards
                WHERE user_id=? AND card_id=?
                LIMIT 1
            )
            """,
            (ctx.author.id, card_id)
        )
        conn.commit()
        conn.close()
        bonus = {"Common": 25, "Uncommon": 75, "Rare": 150, "Epic": 300, "Legendary": 600, "Mythic": 1250}.get(card['rarity'], 50)
        db.add_stellas(ctx.author.id, bonus)
        await ctx.send(f"✅ Merged a duplicate **{card['name']}** into **{bonus}** Stellas! 💫")

async def setup(bot):
    await bot.add_cog(Cards(bot))
