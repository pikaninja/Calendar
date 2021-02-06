import discord
from dependencies import CalendarBot


if __name__ == "__main__":
    description = "A simple bot to view and use a calendar in discord."

    allowed_mentions = discord.AllowedMentions()
    allowed_mentions.roles = False
    allowed_mentions.everyone = False

    intents = discord.Intents.default()
    intents.members = True

    cache = discord.MemberCacheFlags.from_intents(intents)

    bot = CalendarBot(
        command_prefix="cb/",
        description=description,
        allowed_mentions=allowed_mentions,
        intents=intents,
        member_cache_flags=cache,
        activity=discord.Game(name="Watching time pass by."),
        status=discord.Status.idle,
        owner_ids={668906205799907348, 678401615333556277, 671777334906454026}
    )

    bot.run(...) # Token from a config file of some sorts will be here.
    