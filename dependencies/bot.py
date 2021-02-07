import datetime
import humanize
import importlib
import os
import toml
from . import database
from discord.ext import commands


class CalendarBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        print("Calendar Bot is starting!")

        with open("config.toml") as fh:
            self.config = toml.load(fh)

        kwargs.setdefault("owner_ids", self.config.pop("OWNER_IDS", None))
        kwargs.setdefault("command_prefix", self.config.pop("PREFIX", "cb/"))

        self._uptime = datetime.datetime.utcnow()
        self.db = database.create(**self.config["database"])

        super().__init__(*args, **kwargs)
        self._handle_jishaku()

    @property
    def uptime(self):
        return humanize.naturaldelta(datetime.datetime.utcnow() - self._uptime)

    def _handle_jishaku(self):
        message = "Jishaku not found, ignoring flags..."
        jishaku_installed = importlib.util.find_spec("jishaku")
        jishaku_flags = self.config.get("jishaku", False)

        if jishaku_flags and jishaku_installed:
            message = "[LOADED] jishaku"

            for flag, value in jishaku_flags.items():
                os.environ[flag] = str(value)
            self.load_extension("jishaku")
        print(message)

    async def on_ready(self):
        print(f"\nLogged in as: {self.user}")

    async def close(self):
        await self.db.close()
        await super().close()
