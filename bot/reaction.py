import discord
from discord.ext import commands

from database.model import User
from util.config import guild_id, attendance_channel
from database.mongo_client import MongoDBInterface


async def handle_reaction(
    bot: commands.Bot,
    db_client: MongoDBInterface,
    reaction: discord.Reaction,
    user: discord.User,
):
    deduct_points: int = -10  # The points to deduct for a bad emoji reaction
    react_points: int = 3
    receive_points: int = 10
    bad_emojis = [
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
    ]

    # Fetch the message
    message = reaction.message

    # Check if the command is used in the specific server
    if message.guild.id != guild_id:
        return
    await reaction.message.channel.send(f"Reaction: {reaction.emoji} by {user.name}")

    # Fetch the author of the message
    author = message.author
    # If the reaction is from a bot, to a bot's message, from the author themselves, or in the attendance
    # channel, ignore it.
    if (
        attendance_channel == message.channel.id
        or author.bot
        or user.bot
        # or author == user
    ):
        return

    # Fetch the channel object using its ID
    channel = bot.get_channel(attendance_channel)

    emoji = str(reaction.emoji)  # Convert the emoji to string for comparison
    # Deduct points for a bad emoji reaction and send a notification
    if emoji in bad_emojis:
        try:
            # Prepare the user data for updating points
            user_data = dict(
                id=user.id, userName=user.display_name, points=deduct_points
            )
            user = User(**user_data)
            db_client.add_or_update_user_points(user)
            # Formulate the message content
            content = (
                f"<@{user.id}> got 10 points deducted for reacting {emoji} in the <#{message.channel.id}> "
                f"channel."
            )
            # Ensure the channel was found
            if channel:
                # Send the message to the channel
                await channel.send(content)
            else:
                print(f"Could not find the channel with ID: {attendance_channel}")
        except Exception as e:
            print(f"Error while adjusting the user's points: {e}")
        return

    try:
        activity_data = dict(
            dcUsername=user.name,
            dcId=user.id,
            channelId=message.channel.id,
            messageId=message.id,
            activity=ActivityType.react,
            reward=react_points,
            emoji=str(reaction.emoji),
        )
        activity = Activity(**activity_data)
        self.mongo.add_activity(activity)
    except Exception as e:
        print(f"Error while adding the activity: {e}")
    await message.channel.send(f"Reaction: {reaction.emoji} by {user.name}")
