from __future__ import annotations

import asyncio
import contextlib
from os import listdir
from pathlib import Path
from types import SimpleNamespace

from discord import Intents
from discord.ext import commands
from discord.gateway import DiscordWebSocket

import toml
import aiohttp
from rich import print

from utils import ctx
from utils import mobile
from utils.orm import Guilds

from tortoise import Tortoise

from cogwatch import watch

class Bot(commands.Bot):
    def __init__(self, intents=None):
        intents = intents or Intents.all()
        super().__init__(command_prefix=self.dynamic_prefix, intents=intents)
        self.default_prefix = ","
        self.cwd = Path(__file__).resolve().parent.parent
        self._log_startup(f"Current working directory set to: {self.cwd}")
        self.loaded: bool = False
        self.config: SimpleNamespace = self.load_config()
        self.token: str = self.config.keys.TOKEN
        self.web_client: aiohttp.ClientSession = None

        self.database: Tortoise = Tortoise()

        # Apply monkey patches - https://github.com/4rshww/Discord_Phone/
        commands.Context.send_embed = ctx.send_embed
        commands.Context.confirm = ctx.confirm
        DiscordWebSocket.identify = mobile.identify

        self._log_config("Configuration loaded successfully.")

    async def dynamic_prefix(self, bot, message):
        if not message.guild:
            return commands.when_mentioned_or(self.default_prefix)(bot, message)

        guild = await Guilds.get_or_none(guild_id=message.guild.id)

        return commands.when_mentioned_or(guild.prefix if guild and guild.prefix else self.default_prefix)(bot, message)

    def load_config(self):
        config_path = 'config.toml'
        self._log_config(f"Loading configuration from {config_path}...")
        with open(config_path, 'r') as config_file:
            config_data = toml.load(config_file)

        self._log_startup("Configuration loaded. Processing...")
        return self.dict_to_simplenamespace(config_data)

    def dict_to_simplenamespace(self, d):
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = self.dict_to_simplenamespace(value)
        self._log_config("Configuration processed into namespaces.")
        return SimpleNamespace(**d)

    async def setup_hook(self):
        self._log_startup("Loading cogs...")
        for file in listdir(f"./cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                try:
                    await self.load_extension(f"cogs.{file[:-3]}")
                    self._log_startup(f"Loaded cog: {file[:-3]}")
                except Exception as e:
                    self._log_error(f"Failed to load {file[:-3]} cog: {e}")

        self.loaded = True

        self._log_startup(f"[bold bright_white]Logged in as {str(self.user)}[/bold bright_white]")
        try:
            db_config = self.config.db_config
            await self.database.init(
                db_url=f'postgres://{db_config.user}:{db_config.password}@localhost:5432/{db_config.database}',
                modules={'models': ['utils.orm']}
            )
            self._log_database("Connected to the database.")

        except Exception as e:
            self._log_error(f"Failed to connect to the database: {e}")

        current_guild_ids = {guild.id async for guild in self.fetch_guilds()}
        stored_guild_ids = {guild.guild_id for guild in await Guilds.all()}

        new_guilds = current_guild_ids - stored_guild_ids
        for guild_id in new_guilds:
            guild, created = await Guilds.get_or_create(guild_id=guild_id)
            if created:
                self._log_database(f"Added guild {guild.guild_id} to the database")

        guilds_to_remove = stored_guild_ids - current_guild_ids
        for guild_id in guilds_to_remove:
            guild = await Guilds.get(guild_id=guild_id)
            await guild.delete()
            self._log_database(f"Removed guild {guild_id} from the database")

    @watch(path='cogs', preload=False)
    async def on_ready(self):
        pass

    async def main(self) -> None:
        self._log_startup("Bot starting...")
        async with aiohttp.ClientSession() as session:
            self.web_client = session
            async with self:
                await self.start(self.token)

    def starter(self):
        self._log_startup("Bot starter invoked.")
        with contextlib.suppress(KeyboardInterrupt):
            asyncio.run(self.main())

    def _log_startup(self, message: str):
        print(f"[green3][Startup ][/green3] {message}")

    def _log_config(self, message: str):
        print(f"[cyan3][Config  ][/cyan3] {message}")

    def _log_database(self, message: str):
        print(f"[turquoise2][Database][/turquoise2] {message}")

    def _log_error(self, message: str):
        print(f"[red1][Error   ][/red1] {message}")

