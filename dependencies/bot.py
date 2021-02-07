import datetime
import humanize
from discord.ext import commands

class CalendarBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        self._uptime = datetime.datetime.utcnow()
        super().__init__(*args, **kwargs)

    @property
    async def uptime(self):
        return humanize.naturaldelta(datetime.datetime.utcnow() - self._uptime)

    async def on_ready(self):
        print(f"Calendar Bot is starting!\nLogged in as: {self.user}")

