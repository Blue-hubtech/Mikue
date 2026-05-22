import discord
from discord.ext import commands
from database import Database

db = Database()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setchannel", aliases=["setspawnchannel"])
    @commands.has_permissions(administrator=True)
    async def set_spawn_channel(self, ctx, channel: discord.TextChannel = None):
        """Set card spawn channel"""
        channel = channel or ctx.channel
        db.set_config('spawn_channel', str(channel.id))
        await ctx.send(f"✅ Cards will spawn in {channel.mention}!")

    @commands.command(name="setcasino", aliases=["setcasinochannel"])
    @commands.has_permissions(administrator=True)
    async def set_casino_channel(self, ctx, channel: discord.TextChannel = None):
        """Set casino channel"""
        channel = channel or ctx.channel
        db.set_config('casino_channel', str(channel.id))
        await ctx.send(f"✅ Casino games in {channel.mention}!")

    @commands.command(name="setwelcome")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel = None):
        """Set welcome channel"""
        channel = channel or ctx.channel
        db.set_config('welcome_channel', str(channel.id))
        await ctx.send(f"✅ Welcomes in {channel.mention}!")

    @commands.command(name="addstellas")
    @commands.has_permissions(administrator=True)
    async def addstellas(self, ctx, user: discord.User, amount: int):
        """Give Stellas"""
        db.add_stellas(user.id, amount)
        await ctx.send(f"✅ +{amount:,} Stellas to {user.mention}!")

    @commands.command(name="spawn")
    @commands.has_permissions(administrator=True)
    async def spawn(self, ctx):
        """Manual spawn"""
        from bot import spawn_card
        await spawn_card(ctx.channel)

async def setup(bot):
    await bot.add_cog(Admin(bot))
