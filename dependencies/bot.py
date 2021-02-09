import discord
import datetime
import humanize
import importlib
import os
import toml
from . import database
from discord.ext import commands
from .context import Context

initial_extensions = ("cogs.misc",)


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

        for ext in initial_extensions:
            self.load_extension(ext)

    @property
    def uptime(self):
        return humanize.naturaldelta(datetime.datetime.utcnow() - self._uptime)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or Context)

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

    def embed(self, ctx = None, **kwargs):
        kwargs.setdefault("colour", 0xF35B63)
        kwargs.setdefault("timestamp", datetime.datetime.utcnow())
        embed = discord.Embed(**kwargs)

        if ctx:
            embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)

        return embed

    async def on_ready(self):
        print(f"\nLogged in as: {self.user}")

    async def close(self):
        await self.db.close()
        await super().close()
