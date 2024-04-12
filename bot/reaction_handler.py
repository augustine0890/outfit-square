import logging

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
        or author == user
    ):
        return

    # Fetch the designated channel for posting messages about reactions.
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

    # Handle positive reactions for the user who reacted.
    try:
        user_activity_data = {
            "dcUsername": user.name,
            "dcId": user.id,
            "messageId": message.id,
            "activity": ActivityType.REACT,
            "reward": react_points,
            "emoji": emoji,
        }
        activity = Activity(**user_activity_data)
        result: bool = db_client.add_reaction_activity(activity)
        if result:
            user_data = {
                "id": user.id,
                "userName": user.display_name,
                "points": react_points,
            }
            user_model = User(**user_data)
            # Update the user model with new points.
            db_client.add_or_update_user_points(user_model)
            content = f"Yo, <@{user.id}> just scored 3 points for reacting {emoji} on (https://discord.com/channels/{Config.GUILD_ID}/{message.channel.id}/{message.id}) in the <#{message.channel.id}> channel. Keep it up! 🚀"
            await channel.send(content)
    except Exception as e:
        logging.error(f"Error adding user's activity: {e}")

    # Return early if the message is from the announcement channel or ignored channels (no points are granted for
    # author)
    ignored_channels = {Config.ANNOUNCEMENT_CHANNEL_ID, *Config.IGNORED_CHANNEL_IDS}
    if message.channel.id in ignored_channels:
        return

    # Handle positive reactions for the author of the message.
    try:
        author_activity_data = {
            "dcUsername": author.name,
            "dcId": author.id,
            "messageId": message.id,
            "activity": ActivityType.RECEIVE,
            "reward": receive_points,
            "emoji": emoji,
        }
        activity = Activity(**author_activity_data)
        result: bool = db_client.add_reaction_activity(activity)
        if result:
            author_data = {
                "id": author.id,
                "userName": author.display_name,
                "points": receive_points,
            }
            author_model = User(**author_data)
            db_client.add_or_update_user_points(author_model)
            content = (
                f"Heads up, <@{author.id}> got a cool 10 points from <@{user.id}>'s {emoji} reaction on "
                f"(https://discord.com/channels/{Config.GUILD_ID}/{message.channel.id}/{message.id}"
                f") in the <#{message.channel.id}> channel. 🎉👟"
            )
            await channel.send(content)
    except Exception as e:
        logging.error(f"Error adding author's activity: {e}")
