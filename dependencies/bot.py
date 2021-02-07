import toml
import datetime
import humanize
from discord.ext import commands
from . import database


class CalendarBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        with open("config.toml") as fh:
            self.config = toml.load(fh)

        self._uptime = datetime.datetime.utcnow()
        self.db = database.create(**self.config["database"])

        print("Calendar Bot is starting!")
        super().__init__(*args, **kwargs)

        self.load_extension("jishaku")

    @property
    async def uptime(self):
        return humanize.naturaldelta(datetime.datetime.utcnow() - self._uptime)

    async def on_ready(self):
        print(f"Logged in as: {self.user}")

    async def close(self):
        await self.db.close()
        await super().close()
