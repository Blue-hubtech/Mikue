import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        await user.ban(reason=reason)
        embed = discord.Embed(title="🔨 Banned", description=f"{user.mention} was banned.\nReason: {reason}", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        await user.kick(reason=reason)
        embed = discord.Embed(title="👢 Kicked", description=f"{user.mention} was kicked.\nReason: {reason}", color=discord.Color.orange())
        await ctx.send(embed=embed)

    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for ch in ctx.guild.channels:
                await ch.set_permissions(mute_role, send_messages=False, speak=False)
        await user.add_roles(mute_role)
        embed = discord.Embed(title="🔇 Muted", description=f"{user.mention} was muted.\nReason: {reason}", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, user: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role and mute_role in user.roles:
            await user.remove_roles(mute_role)
            await ctx.send(f"🔊 {user.mention} has been unmuted!")
        else:
            await ctx.send("❌ User is not muted!")

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        embed = discord.Embed(title="⚠️ Warning Issued", description=f"{user.mention} was warned.\nReason: {reason}", color=discord.Color.yellow())
        await ctx.send(embed=embed)
        try:
            await user.send(f"⚠️ You were warned in **{ctx.guild.name}**: {reason}")
        except Exception:
            pass

    @commands.command(name="promote")
    @commands.has_permissions(manage_roles=True)
    async def promote(self, ctx, user: discord.Member, *, role_name: str):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"❌ Role **{role_name}** not found!")
            return
        await user.add_roles(role)
        await ctx.send(f"⬆️ {user.mention} promoted to **{role_name}**!")

    @commands.command(name="demote")
    @commands.has_permissions(manage_roles=True)
    async def demote(self, ctx, user: discord.Member, *, role_name: str):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"❌ Role **{role_name}** not found!")
            return
        await user.remove_roles(role)
        await ctx.send(f"⬇️ {user.mention} removed from **{role_name}**!")

    @commands.command(name="open")
    @commands.has_permissions(manage_channels=True)
    async def open_channel(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Channel opened!")

    @commands.command(name="close")
    @commands.has_permissions(manage_channels=True)
    async def close_channel(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Channel closed!")

    @commands.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx, command_name: str):
        cmd = self.bot.get_command(command_name)
        if cmd:
            cmd.enabled = True
            await ctx.send(f"✅ Command `{command_name}` enabled!")
        else:
            await ctx.send(f"❌ Command `{command_name}` not found!")

    @commands.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx, command_name: str):
        if command_name in ["disable", "enable"]:
            await ctx.send("❌ Can't disable this command!")
            return
        cmd = self.bot.get_command(command_name)
        if cmd:
            cmd.enabled = False
            await ctx.send(f"🚫 Command `{command_name}` disabled!")
        else:
            await ctx.send(f"❌ Command `{command_name}` not found!")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
