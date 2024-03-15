import os
import logging

from util.config import Config
import sys

# Import the OutfitSquareBot class
from bot.discord_client import OutfitSquareBot
from database.mongo_client import MongoDBInterface
from util.scheduler import TaskScheduler

if __name__ == "__main__":
    # Configure logging to include the timestamp, log level, and message
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Stage argument
    valid_stages = ["dev", "development"]
    # Default to production environment if no argument is provided
    stage_arg = "prod"
    # Load environment based on command-line argument
    # Check if the "--stage" argument is provided
    if "--stage" in sys.argv:
        try:
            stage_index = sys.argv.index("--stage")
            stage_arg = sys.argv[stage_index + 1].lower()
            # Validate the stage argument
            if stage_arg not in valid_stages:
                logging.error("Invalid stage. The valid stages are: dev, development")
                sys.exit(1)
        except IndexError:
            logging.error("Error: Please provide a value for --stage argument.")
            sys.exit(1)

    # Load '.env' based on specified stage
    Config.load_env(stage_arg)
    # else:
    #     # Default behavior (load prod.env)
    #     load_env("prod")
    logging.info(f"Using {stage_arg.upper()} environment")

    # Load the Discord token
    discord_token = os.getenv("DISCORD_TOKEN")
    if discord_token is None:
        logging.error("Error: DISCORD_TOKEN is not set.")
        sys.exit(1)
    # Load the MongoDB uri
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri is None:
        logging.error("Error: MONGO_URI is not set.")
        sys.exit(1)

    # Establish the MongoDB connection instance
    mongo_client = MongoDBInterface(mongo_uri, "outfit-square")

    # Initialize and run the Bot
    bot = OutfitSquareBot(discord_token, mongo_client)

    # Setup and start the task scheduler
    scheduler = TaskScheduler(database=mongo_client)
    scheduler.setup_schedule()

    # Setup and start the task scheduler, now passing the bot instance
    # scheduler = TaskScheduler(database=mongo_client, bot=bot)

    # Finally, run the Bot
    bot.run_bot()
