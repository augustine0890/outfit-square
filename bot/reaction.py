import discord
from discord.ext import commands

from database.model import User, Activity, ActivityType
from util.config import Config
from database.mongo_client import MongoDBInterface


async def handle_reaction(
    bot: commands.Bot,
    db_client: MongoDBInterface,
    reaction: discord.Reaction,
    user: discord.User,
):
    """Handles reactions on messages according to predefined rules."""
    deduct_points = -10  # Points to deduct for a negative reaction
    react_points = 3  # Points to award for reacting
    receive_points = 10  # Points to award for receiving a reaction

    # Define bad emojis
    bad_emojis = {
        "😠",
        "😤",
        "🤮",
        "💩",
        "🖕🏻",
        "🏻",
        "😾",
        "💢",
        "🇰🇵",
        "👎🏻",
        "👎🏻🏻",
        "😡",
        "👿",
        "🤬",
        "🖕",
        "🖕🏽",
        "👎",
    }

    message = reaction.message

    if message.guild.id != Config.GUILD_ID:
        return

    author = message.author

    # Ignore reactions in certain conditions
    if (
        message.channel.id == Config.ATTENDANCE_CHANNEL_ID
        or author.bot
        or user.bot
        # or author == user
    ):
        return

    channel = bot.get_channel(Config.ATTENDANCE_CHANNEL_ID)

    emoji = str(reaction.emoji)
    if emoji in bad_emojis:
        try:
            user_data = {
                "id": user.id,
                "userName": user.display_name,
                "points": deduct_points,
            }
            user_model = User(**user_data)
            db_client.add_or_update_user_points(user_model)

            content = (
                f"<@{user.id}> got 10 points deducted for reacting {emoji} in "
                f"the <#{message.channel.id}> channel."
            )
            if channel:
                await channel.send(content)
            else:
                print(
                    f"Could not find the channel with ID: {Config.ATTENDANCE_CHANNEL_ID}"
                )
        except Exception as e:
            print(f"Error adjusting points: {e}")
        return

    # Handle adding activity for positive reactions
    try:
        activity_data = {
            "dcUsername": user.name,
            "dcId": user.id,
            "channelId": message.channel.id,
            "messageId": message.id,
            "activity": ActivityType.REACT,
            "reward": react_points,
            "emoji": emoji,
        }
        activity = Activity(**activity_data)
        result: bool = db_client.add_reaction_activity(activity)
        if result:
            user_data = {
                "id": user.id,
                "userName": user.display_name,
                "points": react_points,
            }
            user = User(**user_data)
            db_client.add_or_update_user_points(user)
            content = f"<@{user.id}> got 3 points from reacting {emoji} on (https://discord.com/channels/{Config.GUILD_ID}/{message.channel.id}/{message.id}) in the <#{message.channel.id}> channel."
            await channel.send(content)
    except Exception as e:
        print(f"Error adding activity: {e}")

    # If the message is from the announcement channel, return early (no points are granted for author)
    if message.channel.id == Config.ANNOUNCEMENT_CHANNEL_ID:
        return
