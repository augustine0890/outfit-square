import logging

import discord
from discord.ext import commands

from database.model import User, Activity, ActivityType
from util.config import Config
from database.mongo_client import MongoDBInterface


async def reward_user_contribution(
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

    # Fetch the designated channel for posting messages about contributions.
    bot_channel = bot.get_channel(Config.ATTENDANCE_CHANNEL_ID)

    # Function to determine if the message is from a relevant channel or thread
    def is_relevant_channel(msg):
        if msg.channel.id in channels:
            return msg.channel.id
        if (
            isinstance(msg.channel, discord.Thread)
            and msg.channel.parent_id in channels
        ):
            return msg.channel.parent_id
        return None

    relevant_channel_id = is_relevant_channel(message)
    # Skip if a message is from bot or not in designated channels
    if message.author == bot.user or not relevant_channel_id:
        return

    # Determine if the message contains an image
    msg_contains_image = any(
        attachment.content_type.startswith("image/")
        for attachment in message.attachments
    )

    # Conditions to check for rewarding the activity
    should_reward = False
    reward = channels[relevant_channel_id]["reward"]
    min_length = channels[relevant_channel_id]["min_length"]
    # Split the message content into words and count them
    num_words = len(message.content.split())
    if relevant_channel_id == OOTD_CHANNEL_ID and msg_contains_image:
        should_reward = True
    elif relevant_channel_id == STORE_ADVERTISING_CHANNEL_ID and (
        msg_contains_image or num_words > min_length
    ):
        should_reward = True
    elif relevant_channel_id == UGC_IDEA_CHANNEL_ID and msg_contains_image:
        should_reward = True

    # Process activity if conditions met
    if should_reward:
        await process_contribution_activity(
            message, reward, db_client, bot_channel, bot
        )


async def process_contribution_activity(
    message: discord.Message,
    reward: int,
    db_client: MongoDBInterface,
    bot_channel: discord.channel,
    bot: commands.Bot,
):
    author = message.author
    # Determine channel name
    channel_name = (
        bot.get_channel(message.channel.parent_id).name
        if isinstance(message.channel, discord.Thread)
        else message.channel.name
    )
    try:
        # Create and add activity to a database
        activity_data = {
            "dcUsername": author.name,
            "dcId": author.id,
            "messageId": message.id,
            "channel": channel_name,
            "activity": ActivityType.SHARING,
            "reward": reward,
        }
        activity = Activity(**activity_data)
        result: bool = db_client.add_contribution_activity(activity)
        if result:
            # Update user points
            author_data = {
                "id": author.id,
                "userName": author.display_name,
                "points": reward,
            }
            author_model = User(**author_data)
            db_client.add_or_update_user_points(author_model)

            # Prepare message link and content
            channel_id = (
                message.channel.parent_id
                if isinstance(message.channel, discord.Thread)
                else message.channel.id
            )
            channel_mention = f"<#{channel_id}>"
            message_link = f"https://discord.com/channels/{Config.GUILD_ID}/{channel_id}/{message.id}"
            content = (
                f"Hey, check it out! 🎉<@{author.id}> just bagged {reward} points for sharing cool stuff on "
                f"[this message]({message_link}) in the {channel_mention} channel. Way to go! 🚀👏"
            )

            # Notify in a bot channel about the reward
            await bot_channel.send(content)

    except Exception as e:
        logging.error(f"Error processing activity: {e}")
