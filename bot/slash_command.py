import discord
from discord.ext import commands
from util.config import Config
from util.helper import get_week_number
from database.mongo_client import MongoDBInterface


class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_client = bot.mongo_client

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
        await ctx.respond(message_content, delete_after=60)

    @commands.slash_command(
        guild_ids=[Config.GUILD_ID],
        name="lotto-guideline",
        description="The official guideline for Weekly Lotto",
    )  # Replace with actual guild ID(s)
    async def lotto_guideline(self, ctx: discord.ApplicationContext):
        message_content = (
            ":dress: Welcome to **Outfit Square Weekly Lotto** - where the fashion game is on fire! :slot_machine:\n\n"
            "*How to join? :man_shrugging_tone1:*\n"
            f"1. Head over to the <#{Config.WEEKLY_LOTTO_CHANNEL_ID}> channel.\n"
            "2. Type `/lotto` and pick your lucky 4 single-digit numbers (between 0-9), like '1', '5', '4', '7'.\n"
            "3. Once you're in, you'll get a sweet confirmation message! :incoming_envelope:\n"
            "4. Want to double-check your entry? Just type `/check-lotto` to see your picks for this and last week.\n\n"
            "*Rules :straight_ruler: *\n"
            "- Choose 4 single-digit numbers (between 0-9).\n"
            "- Your numbers need to match both the **value** and **position** of the winning numbers to score.\n"
            "*Example*: Let's say the winning numbers are '0', '6', '0', '6'.\n"
            "- If Mary picked '1', '0', '6', '9' —> 0 matches\n"
            "- If Sally picked '1', '3', '4', '6' —> 1 match\n"
            "- If Tom picked '6', '0', '0', '6' —> 2 matches\n"
            "- If David picked '2', '6', '0', '6' —> 3 matches\n"
            "- If Jenny picked '0', '6', '0', '6' —> 4 matches\n\n"
            "*Prizes :moneybag: *\n"
            "0 matches: No points\n"
            "1 match: 400 points\n"
            "2 matches: 1,000 points\n"
            "3 matches: 5,000 points + Level 1 Badge\n"
            "4 matches: 100,000 points + Level 2 Badge\n"
            "Winners will get a heads-up via DM. :envelope_with_arrow:\n\n"
            "*Participation guidelines :rocket: *\n"
            "- It's totally **free from XX Apr - XX May at 3:00 (UTC+0)**; you can join up to 3 times a week.\n"
            "- After the freebie period, it's 200 points to play; max 5 times a week.\n\n"
            "*When's Game Time? :watch: *\n"
            "- Entries open **Monday 00:00 - Sunday 23:59 (UTC+0)**.\n"
            "- **Every Monday at 03:00 (UTC+0)**, we'll shout out last week's winners.\n\n"
            "Get your game face on - see you at the Weekly Lotto! :tada::crystal_ball:"
        )
        await ctx.respond(message_content, delete_after=60)

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
        if ctx.channel.id != Config.WEEKLY_LOTTO_CHANNEL_ID:
            await ctx.respond(
                f"Please go to the <#{Config.WEEKLY_LOTTO_CHANNEL_ID}> channel to participate in the LOTTO game 🎰",
                delete_after=15,
            )
            return

        # Check if the user has enough points
        user = ctx.author
        fee_points: int = 200
        user_points = self.db_client.get_user_points(user.id)
        if user_points.get("points", 0) < fee_points:
            await ctx.respond(
                "Sorry! You do not have sufficient points to cover the lottery fee. Try to earn more points! "
                "🏋️‍♂️💪🏋️‍♀️",
                ephemeral=True,
            )
            return

        guessed_numbers = [first_number, second_number, third_number, fourth_number]
        # Get the current week number
        current_year, current_week = get_week_number()

        response_message = f"Lotto numbers received: {first_number}, {second_number}, {third_number}, {fourth_number}"
        await ctx.response.send_message(response_message, ephemeral=True)

    @commands.slash_command(name="check-lotto", description="This week's lotto guesses")
    async def check_lotto(self, ctx: discord.ApplicationContext):
        # Get the current week number
        current_year, current_week = get_week_number()
        user_id = ctx.author.id

        # Get the user's lotto guesses

        # If the user hasn't made any guesses yet, send a reminder to participate
        reminder_message = (
            f"Sorry, you haven’t joined the Weekly Lotto this week yet :frowning2:\nType **“/lotto”** "
            f"in <#{Config.WEEKLY_LOTTO_CHANNEL_ID}> channel to try your luck! 🍀"
        )
        # await ctx.response.send_message(reminder_message)

        # If the user has made guesses, construct an embed with the details of their guesses
        await ctx.response.send_message(reminder_message, ephemeral=True)
        return


def setup(bot):
    bot.add_cog(SlashCommands(bot))
