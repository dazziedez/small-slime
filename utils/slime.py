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

from utils import mobile
from utils.orm import Guilds
from utils import ctx
from tortoise import Tortoise

from cogwatch import watch

class Bot(commands.Bot):
    def __init__(self, intents=None):
        intents = intents or Intents.all()
        super().__init__(command_prefix=self.dynamic_prefix, intents=intents)
        self.default_prefix = ","
        self.cwd = Path(__file__).resolve().parent.parent
        print(f"[Startup ] Current working directory set to: {self.cwd}")
        self.loaded = False
        self.config = self.load_config()
        self.token = self.config.keys.TOKEN

        self.database = Tortoise()

        # Apply monkey patches - https://github.com/4rshww/Discord_Phone/
        commands.Context.send_embed = ctx.send_embed
        commands.Context.confirm = ctx.confirm
        DiscordWebSocket.identify = mobile.identify

        print("[Config  ] Configuration loaded successfully.")

    async def dynamic_prefix(self, bot, message):
        if not message.guild:
            return commands.when_mentioned_or(self.default_prefix)(bot, message)

        guild = await Guilds.get_or_none(guild_id=message.guild.id)

        return commands.when_mentioned_or(guild.prefix if guild and guild.prefix else self.default_prefix)(bot, message)

    def load_config(self):
        config_path = 'config.toml'
        print(f"[Config  ] Loading configuration from {config_path}...")
        with open(config_path, 'r') as config_file:
            config_data = toml.load(config_file)

        print("[Startup ] Configuration loaded. Processing...")
        return self.dict_to_simplenamespace(config_data)

    def dict_to_simplenamespace(self, d):
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = self.dict_to_simplenamespace(value)
        print("[Config  ] Configuration processed into namespaces.")
        return SimpleNamespace(**d)

    async def setup_hook(self):
        print("[Startup ] Loading cogs...")
        for file in listdir(f"./cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                try:
                    await self.load_extension(f"cogs.{file[:-3]}")
                    print(f"[Startup ] Loaded cog: {file[:-3]}")
                except Exception as e:
                    print(f"[Error   ] Failed to load {file[:-3]} cog: {e}")

        self.loaded = True
    
        await self.load_extension("jishaku")
        print(f"[Startup ] Logged in as {str(self.user)}")
        try:
            db_config = self.config.db_config
            await self.database.init(
                db_url=f'postgres://{db_config.user}:{db_config.password}@localhost:5432/{db_config.database}',
                modules={'models': ['utils.orm']}
            )
            print("[Database] Connected to the database.")

        except Exception as e:
            print(f"[Database] Failed to connect to the database: {e}")

        current_guild_ids = {guild.id async for guild in self.fetch_guilds()}
        stored_guild_ids = {guild.guild_id for guild in await Guilds.all()}

        new_guilds = current_guild_ids - stored_guild_ids
        for guild_id in new_guilds:
            guild, created = await Guilds.get_or_create(guild_id=guild_id)
            if created:
                print(f"[Database] Added guild {guild.guild_id} to the database")

        guilds_to_remove = stored_guild_ids - current_guild_ids
        for guild_id in guilds_to_remove:
            guild = await Guilds.get(guild_id=guild_id)
            await guild.delete()
            print(f"[Database] Removed guild {guild_id} from the database")

    @watch(path='cogs', preload=False)
    async def on_ready(self):
        pass

    async def main(self) -> None:
        print("[Startup ] Bot starting...")
        async with self:
            await self.start(self.token)

    def starter(self):
        print("[Startup ] Bot starter invoked.")
        with contextlib.suppress(KeyboardInterrupt):
            asyncio.run(self.main())
            print("[Shutdown] Bot has been gracefully shut down.")
