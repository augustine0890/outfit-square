import discord
from discord.ext import commands
from database.mongo_client import MongoDBInterface
from database.model import User, Activity, ActivityType
from datetime import datetime, timezone
from .embed import embed_points_message, embed_rank_message
from .reaction import handle_reaction
from util.config import Config


class OutfitSquareBot(commands.Bot):
    def __init__(self, token, mongo_uri, mongo_dbname):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = (
            True  # Ensure this intent is enabled in your bot's application page
        )
        super().__init__(command_prefix="!", intents=intents)
        self.token = token
        self.mongo_client = MongoDBInterface(mongo_uri, mongo_dbname)

        # Register the commands explicitly
        self.command(name="attend")(self.attend_command)
        self.command(name="check-points", aliases=["cp"])(self.check_points_command)
        self.command(name="my-rank", aliases=["mr"])(self.my_rank)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        await handle_reaction(self, self.mongo_client, reaction, user)

    async def check_points_command(self, ctx, member: discord.Member = None):
        if ctx.guild.id != Config.GUILD_ID:
            return

        if ctx.channel.id != Config.ATTENDANCE_CHANNEL_ID:
            await ctx.reply(
                f"Please go to the <#{Config.ATTENDANCE_CHANNEL_ID}> channel for Daily Attendance and Points Checking."
            )
            return

        member = member or ctx.author
        user_points = self.mongo_client.get_user_points(member.id)
        points_embed = await embed_points_message(member, user_points)
        await ctx.send(embed=points_embed)

    async def my_rank(self, ctx, member: discord.Member = None):
        if ctx.guild.id != Config.GUILD_ID:
            return

        if ctx.channel.id != Config.ATTENDANCE_CHANNEL_ID:
            await ctx.reply(
                f"Please go to the <#{Config.ATTENDANCE_CHANNEL_ID}> channel for Rank Checking."
            )
            return
        # Default to the msg's author if no member is specified
        member = member or ctx.author
        # Retrieve the member's rank
        user_rank: dict = self.mongo_client.get_user_rank(member.id)
        # Check if the member has a rank
        if user_rank["rank"] is not None:
            # The embed message showing the member's rank
            rank_embed = await embed_rank_message(member, user_rank)
            await ctx.send(embed=rank_embed)

    async def attend_command(self, ctx, member: discord.Member = None):
        if ctx.guild.id != Config.GUILD_ID:
            return
        if ctx.channel.id != Config.ATTENDANCE_CHANNEL_ID:
            await ctx.reply(
                f"Please use this command in the <#{Config.ATTENDANCE_CHANNEL_ID}> channel."
            )
            return

        if ctx.author.bot:
            return

        member = member or ctx.author
        user_points = self.mongo_client.get_user_points(member.id)
        points_embed = await embed_points_message(member, user_points)

        today = datetime.utcnow().replace(
            tzinfo=timezone.utc, hour=0, minute=0, second=0, microsecond=0
        )
        count_attendance = self.mongo_client.activity_collection.count_documents(
            {
                "dcId": member.id,
                "activity": ActivityType.ATTEND,
                "createdAt": {"$gte": today},
            }
        )

        if count_attendance > 0:
            await ctx.reply(
                f"<@{member.id}> has already got the daily attendance points today."
            )
            await ctx.send(embed=points_embed)
            return

        if (user_points.get("points", 0) + 50) > Config.MAX_POINTS:
            await ctx.send(
                f"<@{member.id}> You may have reached the maximum limit of {Config.MAX_POINTS} points."
            )
            await ctx.send(embed=points_embed)
            return

        try:
            activity_data = {
                "dcId": member.id,
                "dcUsername": member.name,
                "activity": ActivityType.ATTEND,
                "reward": 50,
            }
            activity = Activity(**activity_data)
            self.mongo_client.add_activity(activity)
            user_data = {"id": member.id, "userName": member.display_name, "points": 50}
            user = User(**user_data)
            self.mongo_client.add_or_update_user_points(user)
            await ctx.reply(
                f"Congratulations <@{member.id}>! You've got 50 points for daily attendance 🎉 See you tomorrow!"
            )
        except Exception as e:
            print(f"Error processing attendance: {e}")
            await ctx.send("An error occurred while marking attendance.")

    def run_bot(self):
        self.run(self.token)
