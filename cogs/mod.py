import discord
from discord.ext import commands

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import slime

class Moderation(commands.Cog):
    """Command group for moderation commands related to guilds."""
    bot: 'slime.Bot'

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.group(name="thread", description="Thread management commands")
    async def thread(self, ctx):
        """Manages threads in the server."""
        return True

    @thread.command(name="lock", description="Locks the current thread")
    @commands.has_permissions(manage_threads=True)
    async def lock(self, ctx: commands.Context):
        """Locks the current thread."""
        if not isinstance(ctx.channel, discord.Thread):
            return await ctx.send_embed(description=f"{ctx.channel.mention} is not a thread.")

        if not ctx.channel.locked:
            await ctx.channel.edit(locked=True)
            await ctx.send_embed(description=f"I have locked {ctx.channel.mention}.")
        else:
            await ctx.send_embed(description=f"{ctx.channel.mention} is already locked.")

    @thread.command(name="unlock", description="Unlocks the current thread")
    @commands.has_permissions(manage_threads=True)
    async def unlock(self, ctx: commands.Context):
        """Unlocks the current thread."""
        if not isinstance(ctx.channel, discord.Thread):
            return await ctx.send_embed(description=f"{ctx.channel.mention} is not a thread.")

        if ctx.channel.locked:
            await ctx.channel.edit(locked=False)
            await ctx.send_embed(description=f"I have unlocked {ctx.channel.mention}.")
        else:
            await ctx.send_embed(description=f"{ctx.channel.mention} is not locked.")

    @commands.group(name="purge", brief="Mention a user to delete messages by them.", description="explod", invoke_without_command=True, aliases=["p", "c", "clear"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, *, args: str = None):
        """Purges messages from the current channel."""
        await ctx.message.delete()
        async with ctx.channel.typing():
            user = None
            limit = 10

            if args:
                parts = args.split()
            else:
                parts = ["10"]
            for part in parts:
                if part.isdigit():
                    limit = int(part)
                else:
                    try:
                        user = await commands.MemberConverter().convert(ctx, part)
                    except commands.MemberNotFound:
                        return

            if not user:
                deleted = await ctx.channel.purge(limit=limit)
                await ctx.send_embed(description=f"{len(deleted)} message{'s' if len(deleted) != 1 else ''} deleted.", reply=False, delete_after=15)
            else:
                messages_due = []
                async for message in ctx.channel.history(limit=100):
                    if message.author == user:
                        messages_due.append(message)

                    if len(messages_due) >= limit:
                        break

                await ctx.channel.delete_messages(messages_due)
                await ctx.send_embed(description=f"{len(messages_due)} message{'s' if len(messages_due) != 1 else ''} by {user.mention} deleted.", reply=False, delete_after=15)

    @purge.command(name="startswith", aliases=["sw"])
    @commands.has_permissions(manage_messages=True)
    async def sw(self, ctx: commands.Context, keyword: str, limit: int):
        """Purges messages that start with a specific keyword."""
        await ctx.message.delete()
        async with ctx.channel.typing():
            messages_due = []

            async for message in ctx.channel.history(limit=100):
                if message.content.lower().startswith(keyword):
                    messages_due.append(message)
                if len(messages_due) >= limit:
                    break

            await ctx.channel.delete_messages(messages_due)
            await ctx.send_embed(description=f'{len(messages_due)} message{"s" if len(messages_due) != 1 else ""} starting with `{keyword}` deleted.', reply=False, delete_after=15)

    @purge.command(name="endswith", aliases=["ew"])
    @commands.has_permissions(manage_messages=True)
    async def ew(self, ctx, keyword: str, limit: int):
        """Purges messages that end with a specific keyword."""
        await ctx.message.delete()
        async with ctx.channel.typing():
            messages_due = []

            async for message in ctx.channel.history(limit=100):
                if message.content.lower().endswith(keyword):
                    messages_due.append(message)
                if len(messages_due) >= limit:
                    break

            await ctx.channel.delete_messages(messages_due)
            await ctx.send_embed(description=f'{len(messages_due)} message{"s" if len(messages_due) != 1 else ""} ending with `{keyword}` deleted.', reply=False, delete_after=15)

    @purge.command(name="bots")
    @commands.has_permissions(manage_messages=True)
    async def bots(self, ctx, limit: int):
        """Purges bot messages."""
        await ctx.message.delete()
        async with ctx.channel.typing():
            messages_due = []

            async for message in ctx.channel.history(limit=100):
                if message.author.bot:
                    messages_due.append(message)
                if len(messages_due) >= limit:
                    break

            await ctx.channel.delete_messages(messages_due)
            await ctx.send_embed(description=f'{len(messages_due)} bot message{"s" if len(messages_due) != 1 else ""} deleted.', reply=False, delete_after=15)

    @purge.command(name="images", brief="Also deletes embed links.", aliases=["img", "media"])
    @commands.has_permissions(manage_messages=True)
    async def img(self, ctx, limit: int):
        """Purges messages with attachments."""
        await ctx.message.delete()
        async with ctx.channel.typing():
            messages_due = []

            async for message in ctx.channel.history(limit=100):
                if message.attachments or message.embeds:
                    messages_due.append(message)
                if len(messages_due) >= limit:
                    break

            await ctx.channel.delete_messages(messages_due)
            await ctx.send_embed(description=f'{len(messages_due)} message{"s" if len(messages_due) != 1 else ""} with attachments deleted.', reply=False, delete_after=15)

    @commands.command(name="pin", brief="Also pins a reply or message id/link.")
    @commands.has_guild_permissions(manage_messages=True)
    async def pin(self, ctx, message=None):
        """Pins the latest message"""
        await self.pin_unpin(ctx, message, True)

    @commands.command(name="unpin", brief="Also unpins a reply or message id/link.")
    @commands.has_guild_permissions(manage_messages=True)
    async def unpin(self, ctx, message=None):
        """Unpins the latest message."""
        await self.pin_unpin(ctx, message, False)

    async def pin_unpin(self, ctx, message, pin):
        if not message:
            if ctx.message.reference:
                replied_message = await ctx.fetch_message(ctx.message.reference.message_id)
                if (replied_message.pinned and pin) or (not replied_message.pinned and not pin):
                    await ctx.send_embed(description=f"The message is already {'pinned' if pin else 'unpinned'}")
                else:
                    if pin:
                        await ctx.message.add_reaction("✅")
                        await replied_message.pin()
                    else:
                        await ctx.message.add_reaction("✅")
                        await replied_message.unpin()
            else:
                async for message in ctx.channel.history(limit=2):
                    if message.id != ctx.message.id:
                        if (message.pinned and pin) or (not message.pinned and not pin):
                            await ctx.send_embed(description=f"The message is already {'pinned' if pin else 'unpinned'}")
                        else:
                            if pin:
                                await message.pin()
                                await ctx.message.add_reaction("✅")
                            else:
                                await message.unpin()
                                await ctx.message.add_reaction("✅")
        else:
            if message.isdigit():
                pin_unpin_message = await ctx.fetch_message(int(message))
            elif message.startswith('https://discord.com/channels/'):
                channel_id, message_id = message.split('/')[-2:]
                channel = self.bot.get_channel(int(channel_id))
                pin_unpin_message = await channel.fetch_message(int(message_id))

            if (pin_unpin_message.pinned and pin) or (not pin_unpin_message.pinned and not pin):
                await ctx.send_embed(description=f"The message is already {'pinned' if pin else 'unpinned'}")
            else:
                if pin:
                    await pin_unpin_message.pin()
                    await ctx.message.add_reaction("✅")
                else:
                    await pin_unpin_message.unpin()
                    await ctx.message.add_reaction("✅")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
