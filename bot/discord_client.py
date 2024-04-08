import logging

import discord
from discord.ext import commands
from database.mongo_client import MongoDBInterface
from database.model import User, Activity, ActivityType, UpdateUserPoints
from datetime import datetime, timezone
from .embed import embed_points_message, embed_rank_message, embed_leaderboard
from .reaction import handle_reaction
from .contribute import handle_contribute
from util.config import Config


class OutfitSquareBot(commands.Bot):
    def __init__(self, token, mongo_client: MongoDBInterface):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = (
            True  # Ensure this intent is enabled in your bot's application page
        )
        super().__init__(command_prefix="!", intents=intents)
        self.token = token
        self.mongo_client = mongo_client

        # Register the commands explicitly
        self.command(name="attend")(self.attend_command)
        self.command(name="check-points", aliases=["cp"])(self.check_points_command)
        self.command(name="rank", aliases=["r"])(self.rank)
        self.command(name="my-rank", aliases=["mr"])(self.my_rank)

        # Load the cog using its module path, adjust "bot.slash_command" as needed for your project structure
        self.load_extension("bot.slash_command")

    async def on_ready(self):
        logging.info(f"Logged in as {self.user}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        await handle_reaction(self, self.mongo_client, reaction, user)

    @commands.Cog.listener()
    async def on_message(self, message):
        await handle_contribute(self, self.mongo_client, message)

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

    async def rank(self, ctx, member: discord.Member = None):
        if ctx.guild.id != Config.GUILD_ID:
            return

        if ctx.channel.id != Config.ATTENDANCE_CHANNEL_ID:
            await ctx.reply(
                f"Hey, don't forget to hit up the <#{Config.ATTENDANCE_CHANNEL_ID}> channel for your rank check. "
                f"Catch you there! 😎"
            )
            return

        # The bot's user
        member = member or ctx.bot.user

        # Retrieve the top users from a database
        success, top_users = self.mongo_client.get_top_ten_users()
        if success:
            # If retrieval is successful, generate and send the leaderboard rank embed
            leaderboard_rank = await embed_leaderboard(member, top_users)
            await ctx.send(embed=leaderboard_rank)

    async def my_rank(self, ctx, member: discord.Member = None):
        if ctx.guild.id != Config.GUILD_ID:
            return

        if ctx.channel.id != Config.ATTENDANCE_CHANNEL_ID:
            await ctx.reply(
                f"Please go to the <#{Config.ATTENDANCE_CHANNEL_ID}> channel for Rank Checking."
            )
            return
        # Default to the msg's author if no member is specified
        member = member or ctx.bot
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
        # Only proceed if attendance hasn't been marked today
        if count_attendance == 0:
            try:
                # Update user points and fetch the updated total
                user_data = {
                    "id": member.id,
                    "userName": member.display_name,
                    "points": 50,
                }
                user = User(**user_data)
                update_status, new_points_total = (
                    self.mongo_client.add_or_update_user_points(user)
                )
                if update_status == UpdateUserPoints.MAX_POINTS_REACHED:
                    # If max points reached, inform the user without adding attendance points
                    await ctx.send(
                        f"<@{member.id}> You may have reached the maximum limit of {Config.MAX_POINTS} points."
                    )
                    return
                else:
                    # On successful points addition, congratulate the user
                    await ctx.reply(
                        f"Congratulations <@{member.id}>! You've got 50 points for daily attendance 🎉 See you tomorrow!"
                    )
                # Display the updated points in an embed, regardless of whether new points were added or max was reached
                points_embed = await embed_points_message(
                    member, {"points": new_points_total}
                )
                await ctx.send(embed=points_embed)

                # Prepare and add the attendance activity
                activity_data = {
                    "dcId": member.id,
                    "dcUsername": member.name,
                    "activity": ActivityType.ATTEND,
                    "reward": 50,
                }
                activity = Activity(**activity_data)
                # Assuming this method correctly adds the activity
                self.mongo_client.add_activity(activity)

            except Exception as e:
                logging.error(f"Error processing attendance: {e}")
                await ctx.send("An error occurred while marking attendance.")

        else:
            user_points = self.mongo_client.get_user_points(member.id)
            # Attendance already marked today, show current points
            points_embed = await embed_points_message(member, user_points)
            await ctx.reply(
                f"<@{member.id}> has already got the daily attendance points today."
            )
            await ctx.send(embed=points_embed)

    def run_bot(self):
        self.run(self.token)
