import discord
from discord import ui


class View(ui.View):
    def __init__(self, author, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.message = None

    async def on_timeout(self) -> None:
        self.disable_all()
        return await super().on_timeout()

    def disable_all(self) -> ui.View:
        for child in self.children:
            if isinstance(child, discord.ui.Item):
                child.disabled = True
        return self

    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your view.", ephemeral=True)
            return False
        
        return await super().interaction_check(interaction)
