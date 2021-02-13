from discord.ext import commands


class CalendarException(Exception):
    pass


class TimeNotParsed(CalendarException):
    """Gets raised whenever a time being parsed has failed."""
    pass


class DuplicateGroup(commands.CommandError):
    """
    Raised when an attempt to create an already existing group is made
    """
    pass
