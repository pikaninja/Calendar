from discord.ext import commands

class Context(commands.Context):
    @property
    def db(self):
        return self.bot.db
