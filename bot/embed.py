import discord
from discord import Embed
from datetime import datetime


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


async def embed_rank_message(member: discord.Member, user_rank: dict) -> Embed:
    """Creates an embed for displaying a member's rank."""
    embed = Embed(title="Your Ranking", colour=0x00AAFF)
    # Set thumbnail, author, and footer using member's avatar and display name
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    embed.set_footer(
        text=f"Given to {member.display_name}", icon_url=member.display_avatar.url
    )
    embed.timestamp = datetime.utcnow()
    # Add a field showing the member's rank and total count
    rank_info = f'{user_rank["rank"]} out of {user_rank["count"]}'
    embed.add_field(name=rank_info, value="Super-Duper! 🎉", inline=True)

    return embed
