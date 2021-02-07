import discord
from dependencies import CalendarBot
from config import token, owner_ids

if __name__ == "__main__":
    description = "A simple bot to view and use a calendar in discord."

    allowed_mentions = discord.AllowedMentions()
    allowed_mentions.roles = False
    allowed_mentions.everyone = False

    intents = discord.Intents.all()

    cache = discord.MemberCacheFlags.from_intents(intents)

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="time pass by."
    )

    bot = CalendarBot(
        command_prefix="cb/",
        description=description,
        allowed_mentions=allowed_mentions,
        intents=intents,
        member_cache_flags=cache,
        activity=activity,
        status=discord.Status.idle,
    )
    bot.owner_ids = set(bot.config["owner_ids"])

    bot.run(bot.config["token"])
