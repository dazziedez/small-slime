import discord

from discord import ui
from discord.ext import commands

from datetime import datetime

from utils.decorators import is_donor
from utils.orm import GuildNicks, Users, Guilds

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import slime

class Utility(commands.Cog):
	"""Command group for utility commands."""
	bot: 'slime.Bot'

	def __init__(self, bot):
		super().__init__()
		self.bot = bot

	@commands.command(brief="beep boop :p")
	async def ping(self, ctx):
		"""Pings the bot."""
		await ctx.send_embed(description=f"🏓 {round(self.bot.latency *  1000)}ms")

	@commands.group(name="membercount", invoke_without_command=True, aliases=["mc"])
	async def mc(self, ctx):
		"""Displays the member count of the guild."""
		if not ctx.guild:
			return await ctx.send_embed(description="Run this command in a guild")

		today = datetime.now().date()
		joined_today = sum(
			1 for member in ctx.guild.members if member.joined_at.date() == today)

		embed = discord.Embed(color=self.bot.config.vars.COLOR)
		embed.set_author(name=f"{ctx.guild.name} (+{joined_today} today)",
						 icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
		embed.add_field(name="Users", value=ctx.guild.member_count)
		embed.add_field(name="Humans", value=sum(
			1 for member in ctx.guild.members if not member.bot))
		embed.add_field(name="Bots", value=sum(
			1 for member in ctx.guild.members if member.bot))

		await ctx.send(embed=embed)

	@mc.command(name="all", brief="Includes bots.")
	async def all(self, ctx):
		"""Displays the total member count across all guilds."""
		all_users = [
			member for guild in self.bot.guilds for member in guild.members]
		await ctx.send_embed(description=f"🔎 I can see **{len(all_users)}** members across **{len(self.bot.guilds)}**")

	@commands.command(name="getbotinvite", aliases=["gbi"])
	async def gbi(self, ctx, bot: discord.User = None, preset: str = "none"):
		"""Generates an invite link for the bot.\nAvaliable presets: `none`, `all`, `admin`, `mod`"""
		presets = {
			"none": 0,
			"all": 70368744177655,
			"admin": 8,
			"mod": 10327212551414
		}
		view = ui.View()

		bot = bot or self.bot.user

		if not bot.bot:
			return await ctx.send_embed(description=f"**{str(bot)}** is not a bot")

		preset = presets.get(preset, 0)

		view.add_item(ui.Button(
			label=f"Invite {str(bot)}", url=f"https://discord.com/api/oauth2/authorize?client_id={bot.id}&scope=bot+applications.commands&permissions={preset}"))
		await ctx.send(view=view)

	@commands.command(name="firstmsg", aliases=["fmsg"])
	async def fmsg(self, ctx):
		"""Displays the first message in the channel."""
		async for m in ctx.channel.history(oldest_first=True, limit=1):
			first_message = m

		if first_message:
			await ctx.send_embed(description=f"Click [here]({first_message.jump_url}) to jump to the first message by {first_message.author.mention}")
		else:
			await ctx.send("No messages found in this channel.")

	@commands.group(name="avatar", invoke_without_command=True, aliases=["av", "pfp"])
	async def av(self, ctx, user: discord.User | discord.Member = None):
		user = user or ctx.author
		await ctx.send_embed(title=user.display_name, image_url=user.display_avatar)

	@av.command(name="guild", aliases=["server"])
	async def guild(self, ctx, user: discord.Member = None):
		user = user or ctx.author
		if not ctx.guild or not user.guild_avatar:
			return await ctx.send_embed(description="This user doesn't have a server avatar")

		await ctx.send_embed(title=user.display_name, image_url=user.guild_avatar)


	@commands.command(name="forcenickname", aliases=["fn"])
	@is_donor()
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
				await user.edit(nick=None)
				return await ctx.send_embed(description=f"Removed forced nickname from {user.mention}")

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
	await bot.add_cog(Utility(bot))
