from discord.ext import commands


class TimeNotParsed(commands.CommandError):
    """Gets raised whenever a time being parsed has failed."""

    def __init__(self, message: str, *args):
        super().__init__(message, *args)