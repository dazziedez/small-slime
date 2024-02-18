import discord
from discord.ext import commands

from utils.orm import Guilds

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import slime

class Servers(commands.Cog):
    """
    A collection of server management commands.
    """
    bot: 'slime.Bot'

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        _, created = await Guilds.get_or_create(guild_id=guild.id)
        if created:
            print(f"[Database] Added guild {guild.name} to the database")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        row, _ = await Guilds.get_or_none(guild_id=guild.id)
        await row.delete()
        print(f"[Database] Removed guild {guild.name} to the database")

    @commands.group(name="prefix", invoke_without_command=True, description="View the server's prefix")
    async def prefix(self, ctx):
        """
        Command group for managing the server's prefix.
        """
        if not ctx.guild:
            return await ctx.send_embed(description="Run this command in a guild")

        guild_id = ctx.guild.id

        guild, created = await Guilds.get_or_create(guild_id=guild_id)
        if guild.prefix and not created:
            await ctx.send_embed(description=f"The prefix for this server is: `{guild.prefix}`")
        else:
            await ctx.send_embed(description=f"The default prefix is: `{self.bot.default_prefix}`")

    @prefix.command(name="set", description="Set the server's prefix")
    async def set_prefix(self, ctx, prefix):
        """
        Command to set the server's prefix.
        """
        if not ctx.guild:
            return await ctx.send_embed(description="Run this command in a guild")

        if len(prefix) > 5:
            return await ctx.send_embed(description="A prefix cannot be longer than **5 characters**")
        guild_id = ctx.guild.id

        guild, _ = await Guilds.get_or_create(guild_id=guild_id)
        guild.prefix = prefix if prefix != self.bot.default_prefix else None
        await guild.save()

        if prefix != self.bot.default_prefix:
            await ctx.send_embed(description=f"Prefix set to: `{prefix}`")
        else:
            await ctx.send_embed(description=f"Removed this guild's prefix")

    @prefix.command(name="remove", description="Remove the server's prefix")
    async def remove_prefix(self, ctx):
        """
        Command to remove the server's prefix.
        """
        if not ctx.guild:
            return await ctx.send_embed(description="Run this command in a guild")

        guild_id = ctx.guild.id

        guild, _ = await Guilds.get_or_create(guild_id=guild_id)
        guild.prefix = None
        await guild.save()

        await ctx.send_embed(description=f"Removed this guild's prefix")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Servers(bot))
