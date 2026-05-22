import discord
from discord.ext import commands
from database import Database
from ranks import get_rank_title, get_xp_for_level, get_next_level_xp, format_progress_bar, get_level_from_xp

db = Database()

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile", aliases=["p"])
    async def profile(self, ctx, user: discord.User = None):
        """View player profile with pic, bio, stats"""
        try:
            target = user or ctx.author
            
            # Get all user data
            stellas = db.get_user_stellas(target.id)
            stats = db.get_user_stats(target.id)
            xp = db.get_user_xp(target.id)
            level = get_level_from_xp(xp)  # Fixed: Use proper XP calculation
            profile_data = db.get_profile(target.id)
            favorite_card = db.get_favorite_card(target.id)
            
            # Profile info
            bio = profile_data.get('bio', 'No bio set.') if profile_data else 'No bio set.'
            profile_pic = profile_data.get('icon') if profile_data else None
            custom_name = profile_data.get('username', target.display_name) if profile_data else target.display_name
            
            # Get user's highest role (only if target is a guild member)
            role = "N/A"
            guild_name = "N/A"
            if isinstance(target, discord.Member):
                role = target.top_role.name
                guild_name = target.guild.name
            
            # Create embed
            embed = discord.Embed(
                title=f"👤 {custom_name}'s Profile",
                color=discord.Color.from_rgb(0, 210, 180)
            )
            
            # Set profile picture or default avatar
            if profile_pic:
                embed.set_thumbnail(url=profile_pic)
            else:
                embed.set_thumbnail(url=target.display_avatar.url)
            
            # Bio section
            embed.add_field(
                name="📝 Bio",
                value=f"```{bio}```",
                inline=False
            )
            
            # Stats section
            embed.add_field(name="💫 Stellas", value=f"`{stellas:,}`", inline=True)
            embed.add_field(name="⭐ Level", value=f"`{level}`", inline=True)
            
            # Fixed: Show XP progress for next level properly
            current_level_xp = get_xp_for_level(level)
            next_level_xp = get_xp_for_level(level + 1) if level < 100 else 0
            current_xp_in_level = xp - current_level_xp
            xp_for_next = next_level_xp - current_level_xp if next_level_xp > 0 else 0
            
            embed.add_field(name="📊 XP", value=f"`{current_xp_in_level}/{xp_for_next}`" if level < 100 else "`MAX LEVEL`", inline=True)
            
            # Cards section
            embed.add_field(name="🎴 Total Cards", value=f"`{stats['total_cards']}`", inline=True)
            embed.add_field(name="⭐ Unique Cards", value=f"`{stats['unique_cards']}`", inline=True)
            embed.add_field(name="📈 Collection", value=f"`{stats['completion_percentage']:.1f}%`", inline=True)
            
            if favorite_card:
                embed.add_field(
                    name="Favorite Card",
                    value=f"**{favorite_card['name']}**\n{favorite_card['series']} - {favorite_card['rarity']}",
                    inline=False
                )
                embed.set_image(url=favorite_card['image_url'])

            # Server info (only show if in guild)
            embed.add_field(name="🏰 Guild", value=f"`{guild_name}`", inline=True)
            embed.add_field(name="👑 Role", value=f"`{role}`", inline=True)
            
            embed.set_footer(text=f"Use .fav <card_id> to feature a favorite card")
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error loading profile: {str(e)}")

    @commands.command(name="setprofilepic", aliases=["setpfp", "setpp"])
    async def set_profile_pic(self, ctx, url: str = None):
        """Set your profile picture"""
        if not url:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                await ctx.send("❌ Please provide an image URL or attach an image!")
                return
        
        # Validate URL
        if not url.startswith('http'):
            await ctx.send("❌ Invalid URL! Must start with http:// or https://")
            return
        
        db.update_profile(ctx.author.id, 'icon', url)
        
        embed = discord.Embed(
            title="✅ Profile Picture Updated!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=url)
        await ctx.send(embed=embed)

    @commands.command(name="resetprofilepic", aliases=["resetpfp", "resetpp"])
    async def reset_profile_pic(self, ctx):
        """Reset profile picture to Discord avatar"""
        db.update_profile(ctx.author.id, 'icon', None)
        await ctx.send("✅ Profile picture reset to your Discord avatar!")

    @commands.command(name="setbio")
    async def setbio(self, ctx, *, bio: str):
        """Set your profile bio"""
        if len(bio) > 200:
            await ctx.send("❌ Bio must be under 200 characters!")
            return
        
        db.update_profile(ctx.author.id, 'bio', bio)
        await ctx.send(f"✅ Bio updated!\n```{bio}```")

    @commands.command(name="resetbio")
    async def resetbio(self, ctx):
        """Reset your bio"""
        db.update_profile(ctx.author.id, 'bio', 'No bio set.')
        await ctx.send("✅ Bio reset!")

    @commands.command(name="setusername", aliases=["setname"])
    async def setusername(self, ctx, *, name: str):
        """Set custom display name for profile"""
        if len(name) > 32:
            await ctx.send("❌ Username must be under 32 characters!")
            return
        
        db.update_profile(ctx.author.id, 'username', name)
        await ctx.send(f"✅ Display name set to **{name}**!")

    @commands.command(name="resetusername", aliases=["resetname"])
    async def resetusername(self, ctx):
        """Reset username to Discord name"""
        db.update_profile(ctx.author.id, 'username', ctx.author.display_name)
        await ctx.send("✅ Username reset to your Discord name!")

    @commands.command(name="rank")
    async def rank(self, ctx, user: discord.User = None):
        """View rank, level, and XP progress"""
        target = user or ctx.author
        level_info = db.get_level_info(target.id)
        total_xp = level_info['xp']
        level = get_level_from_xp(total_xp)  # Fixed: Use proper XP calculation
        
        # Get XP for current and next level
        current_level_xp = get_xp_for_level(level)
        next_level_xp = get_next_level_xp(level)
        current_xp_in_level = total_xp - current_level_xp
        xp_needed = next_level_xp if next_level_xp > 0 else 1
        
        # Get rank title
        title = get_rank_title(level)
        
        # Create progress bar
        progress_bar = format_progress_bar(current_xp_in_level, xp_needed, 15)
        percent = min((current_xp_in_level / xp_needed * 100), 100) if xp_needed > 0 else 100
        
        embed = discord.Embed(
            title=f"{title} {target.display_name}",
            description=f"Level {level}/100",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="📊 Progress to Next Level",
            value=f"`{progress_bar}` {percent:.1f}%",
            inline=False
        )
        
        if level < 100:
            embed.add_field(
                name="💫 Experience",
                value=f"{current_xp_in_level:,}/{xp_needed:,} XP",
                inline=True
            )
        else:
            embed.add_field(
                name="💫 Experience",
                value="MAX LEVEL! 🎉",
                inline=True
            )
        
        embed.add_field(
            name="📈 Total XP",
            value=f"{total_xp:,}",
            inline=True
        )
        
        embed.set_footer(text="Gain XP by using commands! Use .cds to see cooldowns.")
        await ctx.send(embed=embed)

    @commands.command(name="exp", aliases=["xp"])
    async def exp(self, ctx):
        """Check your XP and level"""
        level_info = db.get_level_info(ctx.author.id)
        total_xp = level_info['xp']
        level = get_level_from_xp(total_xp)  # Fixed: Use proper XP calculation
        title = get_rank_title(level)
        await ctx.send(f"{title} **{ctx.author.display_name}**\n💫 Total XP: **{total_xp:,}**")

    @commands.command(name="cds", aliases=["cooldowns"])
    async def check_cooldowns(self, ctx):
        """Check your active command cooldowns"""
        cooldowns = db.get_all_cooldowns(ctx.author.id)
        
        if not cooldowns:
            await ctx.send("✅ No active cooldowns! All commands available.")
            return
        
        embed = discord.Embed(
            title="⏱️ Your Active Cooldowns",
            color=discord.Color.orange()
        )
        
        for command, seconds in sorted(cooldowns.items()):
            minutes = seconds // 60
            secs = seconds % 60
            time_str = f"{minutes}m {secs}s" if minutes > 0 else f"{secs}s"
            embed.add_field(name=f".{command}", value=f"⏰ {time_str}", inline=False)
        
        embed.set_footer(text="Cooldowns prevent command spam and encourage exploration!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
