import discord
from discord.ext import commands
from database.mongo_client import MongoDBInterface
from database.model import User, Activity, ActivityType
from datetime import datetime, timezone
from .embed import embed_points_message


attendance_channel: int = 1021958640829210674  # 1207877436163760198 (outfit-square)
announcement_channel: int = 1209051632655142922  # 1207618904017604668 (outfit-square)
guild_id: int = 1019782712799805440  # 1202064555753353276 (outfit-square)
max_points = 200000


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
        self.command(name="attend")(self.attend)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        deduct_points: int = -10
        react_points: int = 3
        receive_points: int = 10

        # Fetch the message
        message = reaction.message

        # Fetch the author of the message
        author = reaction.message.author
        # If the reaction is from a bot, to a bot's message, from the author themselves, or in the attendance
        # channel, ignore it.
        if (
            attendance_channel == message.channel.id
            or author.bot
            or user.bot
            or author == user
        ):
            return

        try:
            activity_data = dict(
                dcUsername=user.name,
                dcId=user.id,
                channelId=reaction.message.channel.id,
                messageId=reaction.message.id,
                activity=ActivityType.react,
                reward=react_points,
                emoji=str(reaction.emoji),
            )
            activity = Activity(**activity_data)
            self.mongo.add_activity(activity)
        except Exception as e:
            print(f"Error while adding the activity: {e}")
        await reaction.message.channel.send(
            f"Reaction: {reaction.emoji} by {user.name}"
        )

    async def attend(self, ctx, member: discord.Member = None):
        # Check if the command is used in the specific channel
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
