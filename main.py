import os

from utils import load_environment
import sys

# Import the OutfitSquareBot class
from bot.discord_client import OutfitSquareBot

if __name__ == "__main__":
    stage_arg = "prod"  # Default stage
    # Load environment based on command-line argument
    # Check if the "--stage" argument is provided
    if "--stage" in sys.argv:
        try:
            stage_index = sys.argv.index("--stage")
            stage_arg = sys.argv[stage_index + 1].lower()
        except IndexError:
            print("Error: Please provide a value for --stage argument.")
            sys.exit(1)

    # Load '.env' based on specified stage
    load_environment(stage_arg)
    # else:
    #     # Default behavior (load prod.env)
    #     load_environment("prod")
    print(f"Using {stage_arg.upper()} environment")

    # Load the Discord token
    discord_token = os.getenv("DISCORD_TOKEN")
    if discord_token is None:
        print("Error: DISCORD_TOKEN is not set.")
        sys.exit(1)
    # Load the MongoDB uri
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri is None:
        print("Error: MONGO_URI is not set.")
        sys.exit(1)
    # Initialize and run the Bot
    bot = OutfitSquareBot(discord_token, mongo_uri, "outfit-square")
    bot.run_bot()
