import dateparser
from discord.ext import commands
from .errors import *


class TimeConverter(commands.Converter):
    # To be typehinted later because it's beautiful.
    async def convert(self, ctx: ..., arg: str):
        ret = dateparser.parse(arg)

        if not ret:
            fmt = "Failed to parse this time, maybe try reformatting."
            raise TimeNotParsed(fmt)

        return ret