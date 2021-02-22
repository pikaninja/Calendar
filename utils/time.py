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

class PlaceholderConverter(commands.Converter):
    async def convert(self, ctx, arg):
        arg = arg.lower()
        arg = arg.strip("to")
        if " to " in arg and not arg.startswith("to"):
            arg = arg.strip("me inat")
            time, reminder = arg.split(" to ")
            time = dateparser.parse(time.strip())
            return time, reminder.strip()
        arg = arg.replace(" in ", " at ")
        if "at" in arg:
            reminder, time = arg.split(" at ")
            time = dateparser.parse(time.strip())
            return time, reminder.strip()
        trying = arg.split()
        for i in range(len(trying)):
            reminder, time = " ".join(trying[:i]), " ".join(trying[i:])
            print(reminder, "split",  time)
            if time := dateparser.parse(time):
                return time, reminder
