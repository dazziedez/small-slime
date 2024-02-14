import asyncio
import contextlib
from os import listdir
from pathlib import Path
from types import SimpleNamespace

from discord import Intents
from discord.ext import commands
from discord.gateway import DiscordWebSocket

import toml, os

from utils.ui import embeds
from utils import mobile


class Bot(commands.Bot):
    def __init__(self):
        print("[Startup] Initializing bot...")
        super().__init__(intents=Intents.all(), command_prefix=commands.when_mentioned_or(","))

        self.cwd = str(Path(__file__).parents[0].parents[0])
        print(f"[Startup] Current working directory set to: {self.cwd}")
        self.config = self.load_config()

        self.token = os.environ.get("SLIME_TOKEN")

        # monkey patches - https://github.com/4rshww/Discord_Phone/
        commands.Context.send_embed = embeds.send_embed
        DiscordWebSocket.identify = mobile.identify

        print("[Config ] Configuration loaded successfully.")

    def load_config(self):
        config_path = 'config.toml'
        print(f"[Config ] Loading configuration from {config_path}...")
        with open(config_path, 'r') as config_file:
            config_data = toml.load(config_file)

        print("[Startup] Configuration loaded. Processing...")
        return self.dict_to_simplenamespace(config_data)

    def dict_to_simplenamespace(self, d):
        """Recursively converts a dictionary to a SimpleNamespace including nested dictionaries."""
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = self.dict_to_simplenamespace(value)
        print("[Config ] Configuration processed into namespaces.")
        return SimpleNamespace(**d)

    async def setup_hook(self):
        print("[Startup] Loading cogs...")
        for file in listdir(f"./cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                try:
                    await self.load_extension(f"cogs.{file[:-3]}")
                    print(f"[Startup] Loaded cog: {file[:-3]}")
                except Exception as e:
                    print(f"[Error] Failed to load {file[:-3]} cog: {e}")
        await self.load_extension("jishaku")
        print(f"[Startup] Logged in as {str(self.user)}")

    async def main(self) -> None:
        print("[Startup] Bot starting...")
        async with self:
            await self.start(self.token)

    def starter(self):
        print("[Startup] Bot starter invoked.")
        with contextlib.suppress(KeyboardInterrupt):
            asyncio.run(self.main())
            print("[Shutdown] Bot has been gracefully shut down.")

if __name__ == "__main__":
    bot = Bot()
    bot.starter()
