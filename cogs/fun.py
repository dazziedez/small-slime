from discord.ext import commands

import json
import time
import hmac
import base64
import random
import discord
import hashlib
import asyncio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import slime

from bs4 import BeautifulSoup


class Fun(commands.Cog):
    """
    A collection of fun commands.
    """
    bot: 'slime.Bot'

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def randint_fixated(self, range: tuple, id: int | str):
        """
        Generate a random number within a given range, with a fixed seed.
        """
        random.seed(id)
        result = random.randint(range[0], range[1])
        random.seed()
        return result

    @commands.command(name="choose", description="Picks between choices separated by a comma.")
    async def choose(self, ctx, *, choices: str) -> None:
        """
        Picks between choices separated by a comma.
        """

        if len(options := choices.split(",")) <= 1:
            return await ctx.send_embed(description="Enter more than one option please")

        choice = random.choice(options).strip()
        await ctx.send_embed(description=f"I choose `{choice}`")

    @commands.command(name="cute", aliases=["cuteness"])
    async def cute(self, ctx, user: discord.User = None):
        """
        Calculate the cuteness of a user.
        """
        user = user or ctx.author
        await ctx.send_embed(description=f"**{user.mention}**'s cuteness is: `{self.randint_fixated((0, 100), f'{user.id}_cute')}%`")

    @commands.command(name="iq", aliases=["smartness"])
    async def iq(self, ctx, user: discord.User = None):
        """
        Calculate the IQ of a user.
        """
        user = user or ctx.author
        await ctx.send_embed(description=f"**{user.mention}**'s IQ: `{self.randint_fixated((50, 200), f'{user.id}_iq')}`")

    @commands.command(name="ship")
    async def ship(self, ctx, user1: discord.User, user2: discord.User = None):
        """
        Calculate the compatibility of two users.
        """
        user2 = user2 or ctx.author
        await ctx.send_embed(description=f":revolving_hearts: **{user1.mention}** x **{user2.mention}**: `{self.randint_fixated((0, 100), f'{user1.id}{user2.id}_ship')}%`")

    @commands.command(name="cashapp", aliases=["ca"])
    async def cashapp(self, ctx, user):
        """
        Retrieve Cash App information for a user.
        """
        try:
            async with self.bot.web_client.get(f"https://cash.app/${user}") as response:
                if response.status != 200:
                    await ctx.send_embed(description=f"Failed to retrieve data for **{user}**.")
                    return

                content = await response.text()
                profile_json_str = content.split('var profile = ')[
                    1].split(';</script>')[0]
                profile_data = json.loads(profile_json_str)

                display_name = profile_data.get(
                    "display_name", "User not found")
                if display_name == "User not found":
                    await ctx.send_embed(description=f"User **{user}** not found.")
                    return

                await ctx.send_embed(title=display_name, description=f"https://cash.app/${user}", image_url=f"https://cash.app/qr/${user}?size=1024")
        except:
            await ctx.send_embed(description=f"An error occurred while processing **{user}**.")

    @commands.command(name="tokengrab", aliases=["token"], brief="only the first\npart is accurate")
    async def token(self, ctx, user: discord.User = None):
        """
        Generate a unique token for a user.
        """
        user = user or ctx.author
        token = await self.generate_token(user.id, user.created_at)
        await ctx.send_embed(description=f"{user.mention}'s token\n\n`{token}`")

    def encode_base64(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    def decode_base64(self, data):
        data += '=' * (4 - len(data) % 4)
        return base64.urlsafe_b64decode(data.encode('utf-8'))

    async def generate_token(self, user_id, created_at):
        user_b64 = self.encode_base64(str(user_id))

        created_at = int(time.mktime(created_at.timetuple()))
        adjusted_timestamp = created_at - 1293840000
        timestamp_b64 = self.encode_base64(str(adjusted_timestamp))

        secret_key = str(user_id).encode('utf-8')
        message = f'{user_b64}.{timestamp_b64}'.encode('utf-8')

        await asyncio.sleep(0)
        hmac_part = hmac.new(secret_key, message, hashlib.sha256).digest()
        hmac_b64 = self.encode_base64(hmac_part)

        return f'{user_b64}.{timestamp_b64[:5]}.{hmac_b64}'


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
