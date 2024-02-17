from utils.orm import Users
from discord.ext import commands

def is_donor():
    async def predicate(ctx):
        user_data, _ = await Users.get_or_create(user_id=ctx.author.id)
        if user_data and user_data.donor:
            return True
        else:
            return False
    return commands.check(predicate)
