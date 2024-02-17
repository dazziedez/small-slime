import discord
from utils.ui.view import View

class ConfirmationDialog(View):
	def __init__(self, author):
		super().__init__(author)
		self.choice = None

	@discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
	async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.choice = True
		await interaction.response.defer()
		await self.stop()

	@discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
	async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.choice = False
		await interaction.response.defer()
		await self.stop()

	async def on_timeout(self):
		return

async def confirm(self, title, description):
	"""|coro|
	
	Display a confirmation dialog and wait for user input.

	### Parameters:
	- title: The title of the confirmation dialog.
	- description: The description of the confirmation dialog.

	### Returns:
	- The message sent and the user's choice from the confirmation dialog.
	- The user's choice
	"""
	view = ConfirmationDialog(self.author)
	embed = discord.Embed(title=title, description=description)
	msg = await self.reply(embed=embed, view=view)
	await view.wait()
	return msg, view.choice

