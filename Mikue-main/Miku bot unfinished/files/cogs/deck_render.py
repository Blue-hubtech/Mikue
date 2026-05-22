import discord
from discord.ext import commands
from database import Database
import aiohttp
import asyncio
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

db = Database()

RARITY_STYLES = {
    "Common":   {"color": (128,128,128), "border": (160,160,160), "stars": 1, "badge": "C", "glow": False},
    "Uncommon": {"color": (46,204,113),  "border": (46,204,113),  "stars": 2, "badge": "R", "glow": False},
    "Rare":     {"color": (52,152,219),  "border": (52,152,219),  "stars": 3, "badge": "SR","glow": False},
    "Epic":     {"color": (155,89,182),  "border": (155,89,182),  "stars": 4, "badge": "UR","glow": True},
    "Legendary":{"color": (241,196,15),  "border": (241,196,15),  "stars": 5, "badge": "LR","glow": True},
    "Mythic":   {"color": (255,20,147),  "border": (255,20,147),  "stars": 6, "badge": "M", "glow": True}
}

CARD_W, CARD_H = 300, 450
COLUMNS = 3
SPACING = 20
PADDING = 30

class DeckRenderer:
    def __init__(self):
        self.session = None
        self.cache = {}
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def download_image(self, url):
        if url in self.cache:
            return self.cache[url]
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    img = Image.open(io.BytesIO(await resp.read())).convert("RGBA")
                    w, h = img.size
                    s = min(w, h)
                    img = img.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
                    img = img.resize((CARD_W, CARD_H), Image.Resampling.LANCZOS)
                    self.cache[url] = img
                    return img
        except:
            pass
        fallback = Image.new('RGBA', (CARD_W, CARD_H), (40,40,40,255))
        return fallback
    
    async def render(self, cards):
        total = len(cards)
        rows = (total + COLUMNS - 1) // COLUMNS
        full_w = COLUMNS * CARD_W + (COLUMNS - 1) * SPACING + 2*PADDING
        full_h = rows * CARD_H + (rows - 1) * SPACING + 2*PADDING + 60
        canvas = Image.new('RGB', (full_w, full_h), (45,45,55))
        draw = ImageDraw.Draw(canvas)
        
        # Fonts – fallback if missing
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 18)
            series_font = ImageFont.truetype("arial.ttf", 12)
            desc_font = ImageFont.truetype("arial.ttf", 10)
            badge_font = ImageFont.truetype("arialbd.ttf", 20)
        except:
            title_font = ImageFont.load_default()
            series_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
            badge_font = ImageFont.load_default()
        
        draw.text((PADDING, 15), f"⚔️ YOUR DECK • {total}/12 CARDS", fill=(255,255,255), font=title_font)
        
        await self.get_session()
        images = await asyncio.gather(*[self.download_image(c['image_url']) for c in cards])
        
        for idx, card in enumerate(cards):
            r, c = idx // COLUMNS, idx % COLUMNS
            x = PADDING + c * (CARD_W + SPACING)
            y = PADDING + 40 + r * (CARD_H + SPACING)
            style = RARITY_STYLES.get(card['rarity'], RARITY_STYLES['Common'])
            img = images[idx]
            # rounded corners
            mask = Image.new('L', (CARD_W, CARD_H), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle((0,0,CARD_W,CARD_H), radius=20, fill=255)
            img = Image.composite(img, Image.new('RGBA', img.size, (0,0,0,0)), mask)
            canvas.paste(img, (x, y), img)
            # border
            draw.rounded_rectangle((x-2, y-2, x+CARD_W+2, y+CARD_H+2), radius=22, outline=style['border'], width=4)
            # gradient overlay
            overlay = Image.new('RGBA', (CARD_W, CARD_H), (0,0,0,0))
            o_draw = ImageDraw.Draw(overlay)
            for i in range(80, 0, -1):
                alpha = int(160 * (1 - i/80))
                o_draw.rectangle((0, CARD_H-i, CARD_W, CARD_H-i+2), fill=(0,0,0,alpha))
            canvas.paste(overlay, (x, y), overlay)
            # name
            name = card['name'][:20]
            tw = draw.textbbox((0,0), name, font=title_font)[2]
            draw.text((x + (CARD_W - tw)//2, y + 10), name, fill=(255,255,255), font=title_font, stroke_width=1, stroke_fill=(0,0,0))
            # series
            draw.text((x+10, y+CARD_H-40), card['series'][:25], fill=(220,220,220), font=series_font)
            # description
            desc = card.get('description', 'Anime collectible card')
            wrapped = textwrap.wrap(desc, width=28)[:3]
            for i, line in enumerate(wrapped):
                draw.text((x+10, y+CARD_H-25 + i*12), line, fill=(200,200,200), font=desc_font)
            # stars
            stars = "★" * style['stars'] + "☆" * (6 - style['stars'])
            draw.text((x+10, y+CARD_H-8), stars, fill=style['border'], font=desc_font)
            # badge
            badge_x, badge_y = x+8, y+8
            draw.ellipse((badge_x-2, badge_y-2, badge_x+22, badge_y+22), fill=style['border'])
            draw.text((badge_x+3, badge_y+2), style['badge'], fill=(255,255,255), font=badge_font)
        
        buf = io.BytesIO()
        canvas.save(buf, format='PNG')
        buf.seek(0)
        return buf

class DeckRenderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.renderer = DeckRenderer()
    
    @commands.command(name="deck", aliases=["d"])
    async def deck(self, ctx):
        deck = db.get_user_deck(ctx.author.id)
        if not deck:
            await ctx.send("❌ Your deck is empty! Use `.t2d <collection_index>` to add cards.")
            return
        if len(deck) > 12:
            await ctx.send("⚠️ Your deck has too many cards. Remove some with `.t2c <position>`.")
            return
        await ctx.send("🎴 Generating your deck image...")
        try:
            img_bytes = await self.renderer.render(deck)
            file = discord.File(img_bytes, filename="my_deck.png")
            embed = discord.Embed(title=f"⚔️ {ctx.author.display_name}'s Deck", color=discord.Color.gold())
            embed.set_image(url="attachment://my_deck.png")
            embed.set_footer(text=f"{len(deck)}/12 cards • Use .t2d and .t2c")
            await ctx.send(embed=embed, file=file)
        except Exception as e:
            await ctx.send(f"❌ Failed to render deck: {e}")
    
    async def cog_unload(self):
        if self.renderer.session:
            await self.renderer.session.close()

async def setup(bot):
    await bot.add_cog(DeckRenderCog(bot))
