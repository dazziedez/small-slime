import discord

from discord import ui
from discord.ext import commands

from datetime import datetime


class Utility(commands.Cog):
    """Command group for utility commands."""
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Pings the bot."""
        await ctx.reply("hi <@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051><@1161982476143575051>")

    @commands.group(name="membercount", invoke_without_command=True, aliases=["mc"])
    async def mc(self, ctx):
        """Displays the member count of the guild."""
        if not ctx.guild:
            return await ctx.send_embed(description="Run this command in a guild")

        today = datetime.now().date()
        joined_today = sum(
            1 for member in ctx.guild.members if member.joined_at.date() == today)

        embed = discord.Embed(color=self.bot.config.vars.COLOR)
        embed.set_author(name=f"{ctx.guild.name} (+{joined_today} today)",
                         icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.add_field(name="Users", value=ctx.guild.member_count)
        embed.add_field(name="Humans", value=sum(
            1 for member in ctx.guild.members if not member.bot))
        embed.add_field(name="Bots", value=sum(
            1 for member in ctx.guild.members if member.bot))

        await ctx.send(embed=embed)

    @mc.command(name="all")
    async def all(self, ctx):
        """Displays the total member count across all guilds."""
        all_users = [
            member for guild in self.bot.guilds for member in guild.members]
        await ctx.send_embed(description=f"🔎 I can see **{len(all_users)}** members across **{len(self.bot.guilds)}**")

    @commands.command(name="getbotinvite", aliases=["gbi"])
    async def gbi(self, ctx, bot: discord.User = None, preset: str = "none"):
        """Generates an invite link for the bot.\nAvaliable presets: `none`, `all`, `admin`, `mod`"""
        presets = {
            "none": 0,
            "all": 70368744177655,
            "admin": 8,
            "mod": 10327212551414
        }
        view = ui.View()

        bot = bot or self.bot.user

        if not bot.bot:
            return await ctx.send_embed(description=f"**{str(bot)}** is not a bot")

        preset = presets.get(preset, 0)

        view.add_item(ui.Button(
            label=f"Invite {str(bot)}", url=f"https://discord.com/api/oauth2/authorize?client_id={bot.id}&scope=bot+applications.commands&permissions={preset}"))
        await ctx.send(view=view)

    @commands.command(name="firstmsg", aliases=["fmsg"])
    async def fmsg(self, ctx):
        """Displays the first message in the channel."""
        async for m in ctx.channel.history(oldest_first=True, limit=1):
            first_message = m

        if first_message:
            await ctx.send_embed(description=f"Click [here]({first_message.jump_url}) to jump to the first message by {first_message.author.mention}")
        else:
            await ctx.send("No messages found in this channel.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utility(bot))
