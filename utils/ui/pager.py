import discord
import random

from string import ascii_letters
from discord.ui import Button

from utils.ui import view

class PaginatorView(view.View):
    def __init__(self, content, author, delete_on_close=False):
        super().__init__(author, timeout=0)
        self.content = content
        self.author = author
        self.current_page = 0
        self.delete_on_close = delete_on_close

        if isinstance(self.content[0], discord.Embed):
            for i, embed in enumerate(self.content, start=1):
                embed.set_footer(text=f"{i} of {len(self.content)}")
        self.is_embed = isinstance(self.content[0], discord.Embed)

        self.previous_button = Button(custom_id=f"{author.id}_{''.join(i for i in random.choices(ascii_letters, k=15))}",
            emoji="<:previous:1206595324857032765>", style=discord.ButtonStyle.blurple, disabled=True)
        self.previous_button.callback = self.go_to_previous
        self.add_item(self.previous_button)

        self.next_button = Button(custom_id=f"{author.id}_{''.join(i for i in random.choices(ascii_letters, k=15))}",
            emoji="<:next:1206595285711720488>", style=discord.ButtonStyle.blurple, disabled=len(self.content) == 1)
        self.next_button.callback = self.go_to_next
        self.add_item(self.next_button)

        if not self.is_embed:
            self.page_info_button = Button(label=f"Page {self.current_page + 1} of {len(self.content)}", 
                custom_id=f"page_info_{author.id}", style=discord.ButtonStyle.grey, disabled=True)
            self.add_item(self.page_info_button)

        self.jump_button = Button(custom_id=f"{author.id}_{''.join(i for i in random.choices(ascii_letters, k=15))}",
            emoji="<:jumpto:1206595355236499506>", style=discord.ButtonStyle.grey, disabled=len(self.content) == 1)
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
            await self.update_content(interaction)

    async def go_to_next(self, interaction):
        if self.current_page < len(self.content) - 1:
            self.current_page += 1
            await self.update_buttons()
            await self.update_content(interaction)

    async def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.content) - 1
        if hasattr(self, 'page_info_button'):
            self.page_info_button.label = f"Page {self.current_page + 1} of {len(self.content)}"

    async def update_content(self, interaction):
        content = self.content[self.current_page]
        if self.is_embed:
            await interaction.response.edit_message(embed=content, view=self)
        else:
            await interaction.response.edit_message(content=content, view=self)

    async def jump_to(self, interaction):
        paginator_view = self

        class JumpToPageModal(discord.ui.Modal, title="Jump to Page"):
            def __init__(self, content_length, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.content_length = content_length
                self.page_number = discord.ui.TextInput(
                    label="Page Number", placeholder=f"1 / {self.content_length}")
                self.add_item(self.page_number)

            async def on_submit(self, interaction: discord.Interaction):
                if not self.page_number.value.isdigit():
                    return await interaction.response.send_message("Invalid page number.", ephemeral=True)
                page = int(self.page_number.value) - 1
                page = max(0, min(page, self.content_length - 1))

                paginator_view.current_page = page
                await paginator_view.update_buttons()
                await paginator_view.update_content(interaction)

        modal = JumpToPageModal(len(self.content))
        await interaction.response.send_modal(modal)

    async def stop_pages(self, interaction):
        if self.delete_on_close:
            await interaction.message.delete()
            try: await self.stop()
            except: pass
            return
        
        self.disable_all()
        await interaction.response.edit_message(view=self)
        await self.stop()

async def page(ctx, content, reply=True, delete_on_close=True):
    paginator = PaginatorView(content, ctx.author, delete_on_close)
    if isinstance(content[0], discord.Embed):
        first_content = {'embed': content[0]}
    else:
        first_content = {'content': content[0]}
    if reply:
        await ctx.reply(**first_content, view=paginator)
    else:
        await ctx.send(**first_content, view=paginator)
    await paginator.wait()
    await ctx.message.add_reaction("✅")
