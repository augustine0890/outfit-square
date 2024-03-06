import discord
from discord import Embed


async def embed_points_message(member: discord.Member, user_points: dict) -> Embed:
    embed = Embed(title="The Cumulative Points", colour=0x00AAFF)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(
        text=f"Given to {member.display_name}", icon_url=member.display_avatar.url
    )

    # Set the timestamp of the embed
    embed.timestamp = user_points.get("updatedAt")

    # Add a field to the embed
    embed.add_field(
        name=member.name, value=str(user_points.get("points", 0)), inline=True
    )

    return embed
