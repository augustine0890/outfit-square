import discord
from discord.ext import commands
from util.config import Config


class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Example of a guild-specific slash command
    @commands.slash_command(
        guild_ids=[Config.GUILD_ID],
        name="attendance-guideline",
        description="The official guideline for getting the attendance and checking the points",
    )  # Replace with actual guild ID(s)
    async def attendance_guideline(self, ctx: discord.ApplicationContext):
        message_content = (
            "Hey guys, check out our **Discord Bot beta service**- it's lit! :fire: \n"
            ":hugging: Below is what it's all about:\n\n"
            f"**1. Cool Commands :computer:** We've got 4 cool commands in the <#{Config.ATTENDANCE_CHANNEL_ID}> "
            f"channel:\n"
            "a. `!attend` - Pop in daily to Outfit Square Discord.\n"
            "b. `!cp` - See how many points you've racked up.\n"
            "c. `!rank` - Scope out the Cumulative Points TOP 10 Leaderboard.\n"
            "d. `!my-rank` - Check your own points rank.\n\n"
            "**2. Earning Points 101 :notebook_with_decorative_cover:**"
            "a. **Daily Check-ins** :wave_tone1:\n"
            "- Just hit up `!attend` to score 50 points every day. Daily attendance points reset at 00:00 (UTC+0).\n"
            "b. **Emoji Madness** :partying_face:\n"
            "- Dropping an emoji reaction: Earn 3 points (up to 5 times).\n"
            "- Getting emoji love back: Rack up 10 points (up to 10 times).\n"
            "- You can grab a sweet 115 points daily from emojis. Resets at 00:00 (UTC+0).\n\n"
            "**Top Score To Beat** :trophy:\n"
            "During beta, aim for 200,000 points. Once you hit it, no more points for you. Note: This top score might change during beta.\n\n"
            "**Important Points**\n"
            "* Beta means points might get reset when we officially launch.\n"
            "* Points will come in handy for future events and cool stuff.\n\n"
            "We're constantly updating Discord through this beta. Our ultimate goal? Official service with levels and mini-games to boost our community vibes. :earth_americas:\n"
            "Thanks for sticking with us - we're on a mission to make Outfit Square even better for everyone! :purple_heart:"
        )
        await ctx.respond(message_content)

    @commands.slash_command(
        guild_ids=[Config.GUILD_ID],
        name="lotto-guideline",
        description="The official guideline for Weekly Lotto",
    )  # Replace with actual guild ID(s)
    async def lotto_guideline(self, ctx: discord.ApplicationContext):
        # Implement the command logic here

        await ctx.respond("The official guideline for Weekly Lotto")

    @commands.slash_command(name="lotto", description="Weekly Lottery")
    async def lotto(
        self,
        ctx: discord.ApplicationContext,
        first_number: discord.Option(int, "The first number", min_value=0, max_value=9),
        second_number: discord.Option(
            int, "The second number", min_value=0, max_value=9
        ),
        third_number: discord.Option(int, "The third number", min_value=0, max_value=9),
        fourth_number: discord.Option(
            int, "The fourth number", min_value=0, max_value=9
        ),
    ):
        # Implement the command logic here
        response_message = f"Lotto numbers received: {first_number}, {second_number}, {third_number}, {fourth_number}"
        await ctx.response.send_message(response_message, ephemeral=True)


def setup(bot):
    bot.add_cog(SlashCommands(bot))
