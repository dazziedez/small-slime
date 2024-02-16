from discord.ext import commands
import discord
from utils.orm import Guilds, Users, GuildNicks

class Donor(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="forcenickname", aliases=["fn"])
    async def forcenickname(self, ctx, user: discord.Member, *, nick: str = None):
        if not ctx.guild.me.guild_permissions.manage_nicknames:
            return await ctx.send_embed(description="I don't have permission to change nicknames.")
        if not (ctx.guild.owner_id == user.id or ctx.guild.me.top_role > user.top_role):
            return await ctx.send_embed(description="I can't change the nickname of this user.")

        await Users.get_or_create(user_id=user.id)
        await Guilds.get_or_create(guild_id=ctx.guild.id)

        if nick is None:
            usernick = await GuildNicks.filter(user_id=user.id, guild_id=ctx.guild.id).first()
            if usernick:
                await usernick.delete()
                return await ctx.send_embed(description=f"Removed guild nickname from {user.mention}")

        row, created = await GuildNicks.get_or_create(user_id=user.id, guild_id=ctx.guild.id, defaults={'nickname': nick})
        if created and row.nickname != nick:
            row.nickname = nick
            await row.save()

        await user.edit(nick=nick)
        await ctx.send_embed(description=f"Forcing **{row.nickname}** nickname for {user.mention}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick == after.nick:
            return

        user_nick_record = await GuildNicks.filter(guild_id=before.guild.id, user_id=before.id).first()
        if user_nick_record:
            await before.edit(nick=user_nick_record.nickname)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Donor(bot))