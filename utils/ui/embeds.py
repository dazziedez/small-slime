import discord

async def send_embed(self, title=None, description=None, color=None, footer_text=None, footer_icon_url=None, author_name=None, author_url=None, thumbnail_url=None, delete_after=None, reply=True):
    embed = discord.Embed(title=title, description=description, color=color or self.bot.config.vars.COLOR)
    if footer_text or footer_icon_url:
        embed.set_footer(text=footer_text, icon_url=footer_icon_url)
    if author_name or author_url:
        embed.set_author(name=author_name, url=author_url)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    if reply: await self.reply(embed=embed, delete_after=delete_after)
    else: await self.send(embed=embed, delete_after=delete_after)
