import discord
from discord.ext import commands
from database.mongo_client import MongoDBInterface
from database.model import User, Activity, ActivityType
from datetime import datetime, timezone
from .embed import embed_points_message
from .reaction import handle_reaction
from util.config import attendance_channel, announcement_channel, guild_id, max_points


class OutfitSquareBot(commands.Bot):
    def __init__(self, token, mongo_uri, mongo_dbname):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = (
            True  # Ensure this intent is enabled in your bot's application page
        )
        super().__init__(command_prefix="!", intents=intents)
        self.token = token
        self.mongo = MongoDBInterface(mongo_uri, mongo_dbname)

        # Register the commands explicitly
        self.command(name="attend")(self.attend_command)
        self.command(name="check-points", aliases=["cp"])(self.check_points_command)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        db_client = self.mongo
        # Use the handle_reaction function
        # Pass 'self' for the bot argument, since 'self' represents an instance of OutfitSquareBot
        await handle_reaction(self, db_client, reaction, user)

    async def check_points_command(self, ctx, member: discord.Member = None):
        # Check if the command is used in the specific server
        if guild_id != ctx.guild.id:
            return
        if attendance_channel != ctx.channel.id:
            await ctx.message.reply(
                f"<@{ctx.author.id}> Please go to the <#{attendance_channel}> channel for Daily Attendance and Points "
                f"Checking."
            )
            return
        if not member:
            member = ctx.author
        # Check the user's current points
        user_points: dict = self.mongo.get_user_points(member.id)
        points_embed = await embed_points_message(member, user_points)
        # Send the embed in the channel
        await ctx.send(embed=points_embed)
        return

    async def attend_command(self, ctx, member: discord.Member = None):
        # Check if the command is used in the specific server
        if guild_id != ctx.guild.id:
            return
        # Check if the command is used in the specific channel
        if attendance_channel != ctx.channel.id:
            await ctx.message.reply(
                f"<@{ctx.author.id}> Please go to the <#{attendance_channel}> channel for Daily Attendance and Points "
                f"Checking."
            )
            return
        # Check if the author is bot
        if ctx.author.bot:
            return
        if not member:
            member = ctx.author
        # Check the user's current points
        user_points: dict = self.mongo.get_user_points(member.id)
        points_embed = await embed_points_message(member, user_points)

        # Get today's date at midnight in UTC
        today = datetime.utcnow().date()
        # Convert the date object to a datetime object at midnight
        today_datetime = datetime(
            today.year, today.month, today.day, tzinfo=timezone.utc
        )
        count_attendance = self.mongo.activity_collection.count_documents(
            {
                "dcId": member.id,
                "activity": ActivityType.attend,
                "createdAt": {"$gte": today_datetime},
            }
        )
        if count_attendance > 0:
            await ctx.message.reply(
                f"<@{member.id}> has already got the daily attendance points today."
            )
            # Send the embed in the channel
            await ctx.send(embed=points_embed)
            return

        if user_points.get("points") + 50 > max_points:
            await ctx.send(
                f"<@{member.id}> You may have reached the maximum limit of 200,000 points."
            )
            await ctx.send(embed=points_embed)
            return

        # Create an activity
        try:
            activity_data = dict(
                dcId=member.id,
                dcUsername=member.name,
                activity=ActivityType.attend,
                reward=50,
            )
            activity = Activity(**activity_data)
            self.mongo.add_activity(activity)
        except Exception as e:
            print(f"Error while adding the attend activity: {e}")

        try:
            user_data = dict(id=member.id, userName=member.display_name, points=50)
            user = User(**user_data)  # Assuming User class is defined
            self.mongo.add_or_update_user_points(user)
            await ctx.reply(
                f"Congratulations <@{member.id}>! You've got 50 points for daily attendance 🎉 See "
                f"you tomorrow! 👋🏻"
            )
        except Exception as e:
            print(f"Error adding user to database: {e}")
            await ctx.send("An error occurred while marking attendance.")

    def run_bot(self):
        self.run(self.token)
