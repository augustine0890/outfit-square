import discord
from discord.ext import commands
from database.mongo_client import MongoDBInterface
from database.model import User


class OutfitSquareBot(commands.Bot):
    def __init__(self, token, mongo_uri, mongo_dbname):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.token = token
        self.mongo = MongoDBInterface(mongo_uri, mongo_dbname)

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    @commands.command(name='attend')
    async def attend(self, ctx, member: discord.Member = None):
        print(ctx.author.name, ctx.author)
        # If no member is specified, use the command invoker
        if not member:
            member = ctx.author
        # Construct a User model instance
        user_data = {
            "id": member.id,  # Discord ID as _id
            "userName": member.display_name,  # Ensure this matches your User model definition
            "points": 50,
        }
        user = User(**user_data)
        # Perform the database operation
        self.mongo.add_user(user)  # Assuming add_user is not async

        await ctx.send(f"{member.display_name} has been marked as attended.")

    def run_bot(self):
        self.run(self.token)


