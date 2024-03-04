from dotenv import load_dotenv


def load_environment(stage):
    if stage == 'dev':
        load_dotenv("dev.env")
    else:
        load_dotenv("prod.env")
