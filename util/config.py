from dotenv import load_dotenv

attendance_channel: int = 1021958640829210674  # 1207877436163760198 (outfit-square)
announcement_channel: int = 1209051632655142922  # 1207618904017604668 (outfit-square)
guild_id: int = 1019782712799805440  # 1202064555753353276 (outfit-square)
max_points = 200000


def load_environment(stage):
    if stage == "dev":
        load_dotenv("./dev.env")
    else:
        load_dotenv("./prod.env")
