from discord.ext import commands

from fuzzywuzzy import process

import sys
import traceback

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
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_embed(description='You are missing a required argument.')
        elif isinstance(error, commands.BadArgument):
            await ctx.send_embed(description='Invalid argument provided.')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send_embed(description='You do not have permission to use this command.')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send_embed(description='I do not have the required permissions to run this command.')
        elif isinstance(error, commands.CommandNotFound):
            commands_list = [cmd.name for cmd in self.bot.commands]
            closest_match, score = process.extractOne(
                ctx.invoked_with, commands_list)
            if score > 50:
                await ctx.send_embed(description=f"Command not found. Did you mean `{closest_match}`?")
        else:
            await ctx.send_embed(description=error)

        print(
            f'[Error   ] Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
