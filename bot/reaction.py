import discord
from util.config import guild_id


async def handle_reaction(reaction: discord.Reaction, user: discord.User):
    deduct_points: int = -10
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
    if guild_id != message.guild.id:
        return
    await reaction.message.channel.send(f"Reaction: {reaction.emoji} by {user.name}")

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
    await reaction.message.channel.send(f"Reaction: {reaction.emoji} by {user.name}")
