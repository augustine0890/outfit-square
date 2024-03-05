import discord
from discord.ext import commands
from database.mongo_client import MongoDBInterface
from database.model import User


class OutfitSquareBot(commands.Bot):
    def __init__(self, token, mongo_uri, mongo_dbname):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = (
            True  # Ensure this intent is enabled in your bot's application page
        )
        super().__init__(command_prefix="!", intents=intents)
        self.token = token
        self.mongo = MongoDBInterface(mongo_uri, mongo_dbname)

        # Register the commands explicitly
        self.command(name="attend")(self.attend)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def attend(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        try:
            user_data = {
                "id": member.id,
                "userName": member.display_name,
                "points": 50,
            }
            user = User(**user_data)  # Assuming User class is defined
            self.mongo.add_user(user)
            await ctx.send(f"{member.display_name} has been marked as attended.")
        except Exception as e:
            print(f"Error adding user to database: {e}")
            await ctx.send("An error occurred while marking attendance.")

    def run_bot(self):
        self.run(self.token)
