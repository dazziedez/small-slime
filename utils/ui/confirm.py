import discord

from utils.ui import View


class ConfirmationDialog(View):
	def __init__(self, invoke):
		super().__init__(invoke, True)
		self.choice = None
		self.invoke = invoke

	@discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
	async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.choice = True
		await self.stop()

	@discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
	async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.choice = False
		await super().stop()
		await self.stop()

	async def on_timeout(self):
		return


async def send(invoke, title, description):
	"""|coro|
	
	A function that displays a confirmation dialog and waits for user input.

	### Parameters:
	- invoke: The object that triggers the confirmation dialog.
	- title: The title of the confirmation dialog.
	- description: The description of the confirmation dialog.

	### Returns:
	- The user's choice from the confirmation dialog.
	"""
	view = ConfirmationDialog(invoke)
	embed = discord.Embed(title=title, description=description)
	msg = await invoke.reply(embed=embed, view=view)
	await view.wait()
	await msg.delete()
	return view.choice
