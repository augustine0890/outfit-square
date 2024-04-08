import logging

import discord
from discord.ext import commands

from database.model import User, Activity, ActivityType
from util.config import Config
from database.mongo_client import MongoDBInterface


async def handle_contribute(
    bot: commands.Bot,
    db_client: MongoDBInterface,
    message: discord.Message,
):
    # Define channels
    OOTD_CHANNEL_ID = 1207555773010415616  # OOTD Channel
    STORE_ADVERTISING_CHANNEL_ID = 1214380203296686142  # Store Advertising Channel
    UGC_IDEA_CHANNEL_ID = 1207620758814199879  # UGC Idea Channel
    channels = {
        OOTD_CHANNEL_ID: {"reward": 20, "min_length": 0},
        STORE_ADVERTISING_CHANNEL_ID: {"reward": 30, "min_length": 5},
        UGC_IDEA_CHANNEL_ID: {"reward": 30, "min_length": 0},
    }

    # Fetch the designated channel for posting messages about reactions.
    bot_channel = bot.get_channel(Config.ATTENDANCE_CHANNEL_ID)

    # Skip if a message is from bot or not in designated channels
    if message.author == bot.user or message.channel.id not in channels:
        return

    # Determine if the message contains an image
    msg_contains_image = any(
        attachment.content_type.startswith("image/")
        for attachment in message.attachments
    )

    # Conditions to check for rewarding the activity
    should_reward = False
    reward = channels[message.channel.id]["reward"]
    min_length = channels[message.channel.id]["min_length"]
    # Split the message content into words and count them
    num_words = message.content.split()
    if message.channel.id == OOTD_CHANNEL_ID and msg_contains_image:
        should_reward = True
    elif message.channel.id == STORE_ADVERTISING_CHANNEL_ID and (
        msg_contains_image or len(num_words) > min_length
    ):
        should_reward = True
    elif message.channel.id == UGC_IDEA_CHANNEL_ID and msg_contains_image:
        should_reward = True

    # Process activity if conditions met
    if should_reward:
        await process_activity(message, reward, db_client, bot_channel)


async def process_activity(
    message: discord.Message,
    reward: int,
    db_client: MongoDBInterface,
    bot_channel: discord.channel,
):
    author = message.author
    try:
        # Create and add activity to a database
        activity_data = {
            "dcUsername": author.name,
            "dcId": author.id,
            "messageId": message.id,
            "channel": message.channel.name,
            "activity": ActivityType.SHARING,
            "reward": reward,
        }
        activity = Activity(**activity_data)
        result: bool = db_client.add_activity(activity)
        if result:
            # Update user points
            author_data = {
                "id": author.id,
                "userName": author.display_name,
                "points": reward,
            }
            author_model = User(**author_data)
            db_client.add_or_update_user_points(author_model)

            # Notify in a bot channel about the reward
            content = (
                f"Hey, check it out! 🎉<@{author.id}> just bagged {reward} 30 points for sharing cool stuff on ("
                f"https://discord.com/channels/{Config.GUILD_ID}/{message.channel.id}/{message.id}"
                f") in the <#{message.channel.id}> channel. Way to go!🚀👏"
            )
            await bot_channel.send(content)
    except Exception as e:
        logging.error(f"Error processing activity: {e}")
