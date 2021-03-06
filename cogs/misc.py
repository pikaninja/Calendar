import psutil
import discord
import dependencies
from discord.ext import commands
from dependencies import Context

class Misc(commands.Cog):
    """Miscellaneous commands, these part ways from the main objective of the bot."""

    def __init__(self, bot: dependencies.CalendarBot):
        self.bot: dependencies.CalendarBot = bot
        self.process = psutil.Process()

    @commands.command(aliases=["info"])
    async def about(self, ctx: Context):
        """Gives some information about the bot."""

        names = [str(self.bot.get_user(uid)) for uid in self.bot.owner_ids]

        embed = self.bot.embed(ctx)
        embed.title = ", ".join(names)
        embed.set_thumbnail(url=str(ctx.me.avatar_url))

        with self.process.oneshot():
            cpu_percentage = self.process.cpu_percent()

            memory_info = self.process.memory_info()
            memory_percentage = self.process.memory_percent()

            vmem = psutil.virtual_memory()

            memory_repr = f"{(memory_info.rss / 1024 ** 2):,.2f} MB / {(vmem.total / 1024 ** 2):,.2f} MB"

        fields = [
            ["Ping", f"{(self.bot.latency * 1000):,.2f} ms", False],
            ["Uptime", f"{self.bot.uptime}", False],
            ["Guild Count", f"{len(self.bot.guilds)} Guilds", False],
            ["CPU Usage", f"{cpu_percentage}%", False],
            ["Memory Usage", f"{memory_percentage:,.2f}% | {memory_repr}", False],
        ]

        [embed.add_field(name=n, value=v, inline=i) for n, v, i in fields]
        await ctx.send(embed=embed)


def setup(bot: dependencies.CalendarBot):
    bot.add_cog(Misc(bot))
