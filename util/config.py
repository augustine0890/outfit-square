from dotenv import load_dotenv


class Config:
    # Default values for production; can be overridden by load_env
    MAX_POINTS = 200000
    ATTENDANCE_CHANNEL_ID = 1207877436163760198
    ANNOUNCEMENT_CHANNEL_ID = 1207618904017604668
    WEEKLY_LOTTO_CHANNEL_ID = 1214012922825539614
    GUILD_ID = 1202064555753353276
    IGNORED_CHANNEL_IDS = [
        1221744372786266112,
        1207555439458525264,
        1202064555753353278,
    ]  # ugc-sneak-peek, ugc-drops, rules-and-info

    @classmethod
    def load_env(cls, stage: str):
        """Load environment variables based on the specified stage."""
        if stage == "dev":
            cls.ATTENDANCE_CHANNEL_ID = 1021958640829210674
            cls.ANNOUNCEMENT_CHANNEL_ID = 1209051632655142922
            cls.WEEKLY_LOTTO_CHANNEL_ID = 1128945953781579816
            cls.GUILD_ID = 1019782712799805440
            load_dotenv("./dev.env")
        else:  # Default to production environment
            load_dotenv("./prod.env")

        # After loading the .env file, you might want to set MAX_POINTS (and others if necessary) dynamically from
        # the .env as well
        # cls.MAX_POINTS = int(os.getenv("MAX_POINTS", cls.MAX_POINTS))
