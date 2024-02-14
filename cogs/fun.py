from discord.ext import commands
import random

class Fun(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="choose", description="Picks between choices separated by a comma.")
    async def choose(self, ctx, *, choices: str) -> None:
        """Picks between choices separated by a comma."""

        if len(options := choices.split(",")) <= 1:
            return await ctx.send_embed(description="Enter more than one option please")

        choice = random.choice(options).strip()
        await ctx.send_embed(description=f"I choose `{choice}`")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
