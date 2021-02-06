from discord.ext import commands
import datetime
import humanize

class CalanderBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        self._uptime = datetime.datetime.utcnow()
        super().__init__(*args, **kwargs)

    @property
    async def uptime(self):
        return humanize.naturaldelta(datetime.datetime.utcnow()-self._uptime)
