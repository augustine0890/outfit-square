import discord
from discord.ext import commands
from util.config import Config


class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Example of a guild-specific slash command
    @commands.slash_command(
        guild_ids=[Config.GUILD_ID],
        name="lotto-guideline",
        description="The official guideline for Weekly Lotto",
    )  # Replace with actual guild ID(s)
    async def lotto_guideline(self, ctx: discord.ApplicationContext):
        # Implement the command logic here

        await ctx.respond("The official guideline for Weekly Lotto")

    @commands.slash_command(name="lotto", description="Weekly Lottery")
    async def lotto(
        self,
        ctx: discord.ApplicationContext,
        first_number: discord.Option(int, "The first number", min_value=0, max_value=9),
        second_number: discord.Option(
            int, "The second number", min_value=0, max_value=9
        ),
        third_number: discord.Option(int, "The third number", min_value=0, max_value=9),
        fourth_number: discord.Option(
            int, "The fourth number", min_value=0, max_value=9
        ),
    ):
        # Implement the command logic here
        response_message = f"Lotto numbers received: {first_number}, {second_number}, {third_number}, {fourth_number}"
        await ctx.response.send_message(response_message, ephemeral=True)


def setup(bot):
    bot.add_cog(SlashCommands(bot))
