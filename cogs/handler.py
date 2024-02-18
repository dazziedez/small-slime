from discord.ext import commands

from fuzzywuzzy import process

import sys
import traceback

from rich import print

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import slime


class ErrorHandler(commands.Cog):
    bot: 'slime.Bot'

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        match error:
            case isinstance(error, commands.MissingRequiredArgument):
                await ctx.send_embed(description='You are missing a required argument.')
            case isinstance(error, commands.BadArgument):
                await ctx.send_embed(description='Invalid argument provided.')
            case isinstance(error, commands.CheckFailure):
                await ctx.send_embed(description='You are not allowed to use this command.')
            case isinstance(error, commands.MissingPermissions):
                await ctx.send_embed(description='You do not have permission to use this command.')
            case isinstance(error, commands.BotMissingPermissions):
                await ctx.send_embed(description='I do not have the required permissions to run this command.')
            case isinstance(error, commands.CommandNotFound):
                commands_list = [cmd.name for cmd in self.bot.commands]
                closest_match, score = process.extractOne(
                    ctx.invoked_with, commands_list)
                if score > 50:
                    await ctx.send_embed(description=f"Command not found. Did you mean `{closest_match}`?")
            case _:
                await ctx.send_embed(description=error)

        print(f'[red1][Error   ][/red1] Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
