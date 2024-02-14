from discord.ext import commands
from discord.ext.commands import HelpCommand
from utils.ui.pager import page
import discord


class CustomHelpCommand(HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={'aliases': ['h', 'commands'], 'brief': 'hi'})

    async def send_bot_help(self, mapping):
        embeds = [await self.create_cog_embed(cog, commands) for cog, commands in mapping.items() if commands]
        await page(self.context, embeds)

    async def create_cog_embed(self, cog, commands):
        embed_title = cog.qualified_name if cog else 'No Category'
        embed_description = f"{cog.description if cog else ''}\n\n"
        filtered_commands = await self.filter_commands(commands, sort=True)
        command_signatures = [
            f"`{command.name}`" for command in filtered_commands]
        embed_description += ", ".join(command_signatures)
        return discord.Embed(title=embed_title, description=embed_description, color=self.context.bot.config.vars.COLOR)

    async def send_cog_help(self, cog):
        filtered_commands = await self.filter_commands(cog.get_commands(), sort=True)
        embeds = []
        for command in filtered_commands:
            if not command.parents:
                embed = discord.Embed(
                    title=f"{cog.qualified_name} - {command.name}", description="", color=self.context.bot.config.vars.COLOR)

                aliases = ", ".join(
                    command.aliases) if command.aliases else "No aliases"

                usage = self.get_command_signature(command)
                embed.add_field(name="Aliases", value=aliases, inline=True)
                embed.add_field(name="Info", value=command.brief or "Nop", inline=True)
                embed.add_field(
                    name="Usage", value=f"```{usage}```", inline=False)

                embeds.append(embed)

        await page(self.context, embeds)

    async def send_group_help(self, group):
        embeds = []
        filtered_commands = await self.filter_commands(group.commands, sort=True)

        if group.invoke_without_command:
            embed = discord.Embed(
                title=f"{group.cog.qualified_name} - {group.qualified_name}", description=group.help or "No description provided.", color=self.context.bot.config.vars.COLOR)

            embed.add_field(name="Aliases", value=", ".join(
                group.aliases) if group.aliases else "No aliases", inline=True)

            embed.add_field(
                name="Info", value=group.brief or "Nop", inline=True)

            embed.add_field(
                name="Usage", value=f"```{self.get_command_signature(group)}```", inline=False)

            embeds.insert(0, embed)

        for command in filtered_commands:
            embed = discord.Embed(title=f"{group.qualified_name} - {command.name}",
                                  description=command.help or "No description provided.", color=self.context.bot.config.vars.COLOR)

            embed.add_field(name="Aliases", value=", ".join(
                command.aliases) if command.aliases else "No aliases", inline=True)

            embed.add_field(
                name="Info", value=command.brief or "Nop", inline=True)

            embed.add_field(
                name="Usage", value=f"```{self.get_command_signature(command)}```", inline=False)

            embeds.append(embed)

        await page(self.context, embeds)

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"{command.qualified_name}",
                              description=command.help or "No description", color=self.context.bot.config.vars.COLOR)
        aliases = ", ".join(
            command.aliases) if command.aliases else "No aliases"
        usage = f"```{self.get_command_signature(command)}```"
        embed.add_field(name="Aliases", value=aliases, inline=True)
        embed.add_field(
            name="Info", value=command.brief or "Nop", inline=True)
        embed.add_field(name="Usage", value=usage, inline=False)

        await self.context.reply(embed=embed)

    async def send_error_message(self, error: str) -> None:
        await self.context.send_embed(description=error)

async def setup(bot):
    bot.help_command = CustomHelpCommand()
