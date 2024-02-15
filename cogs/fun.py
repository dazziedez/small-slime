from discord.ext import commands
import random
import discord

class Fun(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot

    def randint_fixated(self, range:tuple, id:int|str):
        random.seed(id)
        result = random.randint(range[0], range[1])
        random.seed()
        return result

    @commands.command(name="choose", description="Picks between choices separated by a comma.")
    async def choose(self, ctx, *, choices: str) -> None:
        """Picks between choices separated by a comma."""

        if len(options := choices.split(",")) <= 1:
            return await ctx.send_embed(description="Enter more than one option please")

        choice = random.choice(options).strip()
        await ctx.send_embed(description=f"I choose `{choice}`")

    @commands.command(name="cute", aliases=["cuteness"])
    async def cute(self, ctx, user: discord.User = None):
        user = user or ctx.author
        await ctx.send_embed(description=f"**{str(user)}**'s cuteness is: `{self.randint_fixated((0, 100), f'{user.id}_cute')}%`")

    @commands.command(name="iq", aliases=["smartness"])
    async def iq(self, ctx, user: discord.User = None):
        user = user or ctx.author
        await ctx.send_embed(description=f"**{str(user)}**'s IQ: `{self.randint_fixated((50, 200), f'{user.id}_iq')}`")

    @commands.command(name="ship")
    async def ship(self, ctx, user1: discord.User, user2: discord.User = None):
        user2 = user2 or ctx.author
        await ctx.send_embed(description=f":revolving_hearts: **{str(user1)}** x **{str(user2)}**: `{self.randint_fixated((0, 100), f'{user1.id}{user2.id}_ship')}%`")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
