from discord.ext import commands
import discord
from utils.orm import Users

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import slime

class Donor(commands.Cog):
    bot: 'slime.Bot'

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.group(name="donor", description="Manage donors")
    @commands.is_owner()
    async def donor(self, _):
        return False

    @donor.command(name="add", description="Give a member donor perks")
    async def d_add(self, ctx, user: discord.User):
        await Users.update_or_create(user_id=user.id, defaults={'donor': True})
        await ctx.send_embed(description=f"{user.mention} is now a donor")

    @donor.command(name="remove", description="Remove a member's donor perks")
    async def d_remove(self, ctx, user: discord.User):
        donor = await Users.get_or_none(user_id=user.id)
        if not donor or not donor.donor:
            return await ctx.send_embed(description=f"{user.mention} was not a donor")

        donor.donor = False
        await donor.save()
        await ctx.send_embed(description=f"{user.mention} is no longer a donor")

    @donor.command(name="inspect", aliases=["check"], description="Give a member donor perks")
    async def d_check(self, ctx, user: discord.User):
        donor = await Users.get_or_none(user_id=user.id)
        if not donor or not donor.donor:
            return await ctx.send_embed(description=f"{user.mention} is not a donor")
        await ctx.send_embed(description=f"{user.mention} is a donor")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Donor(bot))