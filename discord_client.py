import discord
from discord.ext import commands


class OutfitSquareBot(commands.Bot):
    def __init__(self, token):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.token = token

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    def run_bot(self):
        self.run(self.token)
