import discord
from discord.ext import commands
from ai_personality import get_ai_response
import random

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ai")
    async def ai(self, ctx, *, text: str):
        async with ctx.typing():
            response = await get_ai_response(text, ctx.author.display_name)
        await ctx.reply(response)

    @commands.command(name="translate")
    async def translate(self, ctx, *, text: str):
        await ctx.send("🌐 Translation requires `googletrans` or DeepL API. Add to `.env` to enable!")

    @commands.command(name="weather")
    async def weather(self, ctx, *, city: str):
        embed = discord.Embed(title=f"🌤️ Weather: {city}", description="Add `WEATHER_API_KEY` (openweathermap.org) to `.env` to enable live weather!", color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(name="define")
    async def define(self, ctx, *, word: str):
        import urllib.request, json
        try:
            url  = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            with urllib.request.urlopen(url) as r:
                data = json.loads(r.read())[0]
            meaning  = data['meanings'][0]['definitions'][0]['definition']
            part     = data['meanings'][0]['partOfSpeech']
            embed    = discord.Embed(title=f"📖 {word.capitalize()}", color=discord.Color.blue())
            embed.add_field(name=part, value=meaning, inline=False)
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send(f"❌ Definition for **{word}** not found!")

    @commands.command(name="urbandic")
    async def urbandic(self, ctx, *, word: str):
        await ctx.send(f"🏙️ Urban Dictionary search for **{word}** — API integration coming soon!")

    @commands.command(name="horoscope")
    async def horoscope(self, ctx, sign: str):
        signs   = ["aries","taurus","gemini","cancer","leo","virgo","libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
        sign    = sign.lower()
        if sign not in signs:
            await ctx.send(f"❌ Invalid sign! Choose from: {', '.join(signs)}")
            return
        fortunes = ["Great things are coming your way~! 🌟","Be cautious today, Miku senses trouble! ⚠️","Love and luck are on your side! 💕","Stay focused — your hard work will pay off! 💪","A surprise awaits you soon! 🎁","You will achieve great things! ✨"]
        embed = discord.Embed(title=f"🔮 {sign.capitalize()} Horoscope", description=random.choice(fortunes), color=discord.Color.purple())
        await ctx.send(embed=embed)

    @commands.command(name="bible")
    async def bible(self, ctx, *, verse: str):
        await ctx.send(f"✝️ Bible verse lookup for **{verse}** — API integration coming soon!")

    @commands.command(name="quran")
    async def quran(self, ctx, *, verse: str):
        await ctx.send(f"☪️ Quran verse lookup for **{verse}** — API integration coming soon!")

    @commands.command(name="emoji")
    async def emoji_info(self, ctx, *, name: str):
        await ctx.send(f"😊 Emoji info for **{name}** — coming soon!")

    @commands.command(name="emojimix")
    async def emojimix(self, ctx, *, combo: str):
        emojis = combo.split("+")
        await ctx.send(f"✨ Emoji mix: {' + '.join(emojis)} = 🎉 (Google Emoji Kitchen API coming soon!)")

    @commands.command(name="sticker")
    async def sticker(self, ctx, url: str = None):
        await ctx.send("🖼️ Sticker creation coming soon!")

    @commands.command(name="toimage")
    async def toimage(self, ctx):
        await ctx.send("🖼️ Sticker to image conversion coming soon!")

    @commands.command(name="upload")
    async def upload(self, ctx, url: str = None):
        await ctx.send("📤 File upload coming soon!")

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        color   = discord.Color.green() if latency < 100 else (discord.Color.yellow() if latency < 200 else discord.Color.red())
        embed   = discord.Embed(title="🏓 Pong!", description=f"**{latency}ms**", color=color)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utils(bot))
