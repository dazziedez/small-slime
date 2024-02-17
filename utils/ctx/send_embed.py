import discord
from utils.ui.view import View

async def send_embed(self, title:str=None, description:str=None, color:hex=None, footer_text:str=None, footer_icon_url:str=None, author_name:str=None, author_url:str=None, thumbnail_url:str=None, image_url:str=None, delete_after:float=None, reply:bool=True):
    embed = discord.Embed(title=title, description=description, color=color or self.bot.config.vars.COLOR)
    if footer_text or footer_icon_url:
        embed.set_footer(text=footer_text, icon_url=footer_icon_url)
    if author_name or author_url:
        embed.set_author(name=author_name, url=author_url)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if image_url:
        embed.set_image(url=image_url)
    
    if reply: await self.reply(embed=embed, delete_after=delete_after)
    else: await self.send(embed=embed, delete_after=delete_after)
