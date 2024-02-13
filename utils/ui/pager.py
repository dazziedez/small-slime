import discord
import random

from string import ascii_letters
from discord.ui import Button

from utils.ui import view

class PaginatorView(view.View):
    def __init__(self, embeds, author):
        super().__init__(author, timeout=0)
        self.embeds = embeds
        self.author = author
        self.current_page = 0

        for i, embed in enumerate(self.embeds, start=1):
            embed.set_footer(text=f"{i} of {len(self.embeds)}")
        
        self.previous_button = Button(custom_id=f"{author.id}_{''.join(i for i in random.choices(ascii_letters, k=15))}",
            emoji="<:previous:1206595324857032765>", style=discord.ButtonStyle.blurple, disabled=True)
        self.previous_button.callback = self.go_to_previous
        self.add_item(self.previous_button)

        self.next_button = Button(custom_id=f"{author.id}_{''.join(i for i in random.choices(ascii_letters, k=15))}",
            emoji="<:next:1206595285711720488>", style=discord.ButtonStyle.blurple)
        self.next_button.callback = self.go_to_next
        self.add_item(self.next_button)

        self.jump_button = Button(custom_id=f"{author.id}_{''.join(i for i in random.choices(ascii_letters, k=15))}",
            emoji="<:jumpto:1206595355236499506>", style=discord.ButtonStyle.grey)
        self.jump_button.callback = self.jump_to
        self.add_item(self.jump_button)

        self.close_button = Button(custom_id=f"{author.id}_{''.join(i for i in random.choices(ascii_letters, k=15))}",
            emoji="<:close:1206595397628203028>", style=discord.ButtonStyle.red)
        self.close_button.callback = self.stop_pages
        self.add_item(self.close_button)

    async def go_to_previous(self, interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_buttons()
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    async def go_to_next(self, interaction):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await self.update_buttons()
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    async def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1

    async def jump_to(self, interaction):
        paginator_view = self

        class JumpToPageModal(discord.ui.Modal, title="Jump to Page"):
            def __init__(self, embeds_length, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.embeds_length = embeds_length
                self.page_number = discord.ui.TextInput(
                    label="Page Number", placeholder=f"1 / {self.embeds_length}")
                self.add_item(self.page_number)

            async def on_submit(self, interaction: discord.Interaction):
                if not self.page_number.value.isdigit():
                    return await interaction.response.send_message("Invalid page number.", ephemeral=True)
                page = int(self.page_number.value) - 1
                page = max(0, min(page, self.embeds_length - 1))

                paginator_view.current_page = page
                await paginator_view.update_buttons()
                await interaction.response.edit_message(embed=paginator_view.embeds[page], view=paginator_view)

        modal = JumpToPageModal(len(self.embeds))
        await interaction.response.send_modal(modal)

    async def stop_pages(self, interaction):
        self.disable_all()
        await interaction.response.edit_message(view=self)


async def page(ctx, embeds, reply=True):
    paginator = PaginatorView(embeds, ctx.author)
    if reply: await ctx.reply(embed=embeds[0], view=paginator)
    else: await ctx.send(embed=embeds[0], view=paginator)
