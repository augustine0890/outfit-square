from utils import load_environment
import sys
import os

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
        load_environment(stage_arg)
    # else:
    #     # Default behavior (load prod.env)
    #     load_environment("prod")
    dc_token = os.getenv("DISCORD_TOKEN")

    print(f"Using {stage_arg.upper()} environment")
    print(f"DISCORD TOKEN: {dc_token}")
