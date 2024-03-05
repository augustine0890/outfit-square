import discord
from discord.ext import commands
from database.mongo_client import MongoDBInterface
from database.model import User, Activity, ActivityType

attendance_channel: int = 1021958640829210674  # 1207877436163760198 (outfit-square)
announcement_channel: int = 1209051632655142922  # 1207618904017604668(outfit-square)


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
            activity_data = {
                "dcUsername": user.name,
                "channelId": reaction.message.channel.id,
                "messageId": reaction.message.id,
                "activity": ActivityType.react,
                "reward": react_points,
                "emoji": str(reaction.emoji),
            }
            activity = Activity(**activity_data)
            self.mongo.add_activity(activity)
        except Exception as e:
            print(f"Error while adding the activity: {e}")
        await reaction.message.channel.send(
            f"Reaction: {reaction.emoji} by {user.name}"
        )

    async def attend(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        try:
            user_data = {
                "id": member.id,
                "userName": member.display_name,
                "points": 50,
            }
            user = User(**user_data)  # Assuming User class is defined
            self.mongo.add_user(user)
            await ctx.send(f"{member.display_name} has been marked as attended.")
        except Exception as e:
            print(f"Error adding user to database: {e}")
            await ctx.send("An error occurred while marking attendance.")

    def run_bot(self):
        self.run(self.token)