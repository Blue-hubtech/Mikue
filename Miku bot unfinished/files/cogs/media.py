import discord
from discord.ext import commands
import random

class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lyrics")
    async def lyrics(self, ctx, *, song: str):
        embed = discord.Embed(title=f"🎵 Lyrics: {song}", description="Lyrics search requires a lyrics API (e.g. genius.com API).\nAdd your `GENIUS_API_KEY` to `.env` to enable this!", color=discord.Color.blue())
        embed.set_footer(text="Feature ready — just needs API key!")
        await ctx.send(embed=embed)

    @commands.command(name="song")
    async def song(self, ctx, *, query: str):
        embed = discord.Embed(title=f"🎶 Song Search: {query}", description="Connect a music API (Spotify/Deezer) to enable song search!", color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(name="spotify")
    async def spotify(self, ctx, *, user: str = None):
        await ctx.send("🎧 Spotify integration coming soon! Add `SPOTIFY_CLIENT_ID` to `.env`")

    @commands.command(name="ytv")
    async def ytv(self, ctx, *, query: str):
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        embed = discord.Embed(title=f"📺 YouTube: {query}", description=f"[Search YouTube]({url})", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(name="yts")
    async def yts(self, ctx, *, query: str):
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}+song"
        embed = discord.Embed(title=f"🎵 YouTube Music: {query}", description=f"[Search YouTube Music]({url})", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(name="tiktok")
    async def tiktok(self, ctx, url: str):
        await ctx.send("📱 TikTok downloader requires a third-party API. Coming soon!")

    @commands.command(name="igdl")
    async def igdl(self, ctx, url: str):
        await ctx.send("📸 Instagram downloader requires a third-party API. Coming soon!")

    @commands.command(name="facebook")
    async def facebook(self, ctx, url: str):
        await ctx.send("📘 Facebook downloader requires a third-party API. Coming soon!")

    @commands.command(name="x")
    async def x(self, ctx, url: str):
        await ctx.send("🐦 X/Twitter downloader requires a third-party API. Coming soon!")

    @commands.command(name="pinterest")
    async def pinterest(self, ctx, *, query: str):
        url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '+')}"
        embed = discord.Embed(title=f"📌 Pinterest: {query}", description=f"[Search Pinterest]({url})", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(name="threads")
    async def threads(self, ctx, url: str = None):
        await ctx.send("🧵 Threads viewer coming soon!")


async def setup(bot):
    await bot.add_cog(Media(bot))
