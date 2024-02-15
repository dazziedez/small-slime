from discord.ext import commands
from discord import app_commands

from utils.orm import Guilds

class Servers(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix", invoke_without_command=True, description="View the server's prefix")
    async def prefix(self, ctx):
        if not ctx.guild:
            return await ctx.send_embed(description="Run this command in a guild")

        guild_id = ctx.guild.id

        guild, created = await Guilds.get_or_create(id=guild_id)
        if guild.prefix and not created:
            await ctx.send_embed(description=f"The prefix for this server is: `{guild.prefix}`")
        else:
            await ctx.send_embed(description=f"The default prefix is: `{self.bot.default_prefix}`")

    @prefix.command(name="set", description="Set the server's prefix")
    async def set_prefix(self, ctx, prefix):
        if not ctx.guild:
            return await ctx.send_embed(description="Run this command in a guild")

        guild_id = ctx.guild.id

        guild, _ = await Guilds.get_or_create(id=guild_id)
        guild.prefix = prefix if prefix != self.bot.default_prefix else None
        await guild.save()

        if prefix != self.bot.default_prefix:
            await ctx.send_embed(description=f"Prefix set to: `{prefix}`")
        else:
            await ctx.send_embed(description=f"Removed this guild's prefix")

    @prefix.command(name="remove", description="Remove the server's prefix")
    async def remove_prefix(self, ctx):
        if not ctx.guild:
            return await ctx.send_embed(description="Run this command in a guild")

        guild_id = ctx.guild.id

        guild, _ = await Guilds.get_or_create(id=guild_id)
        guild.prefix = None
        await guild.save()

        await ctx.send_embed(description=f"Removed this guild's prefix")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Servers(bot))