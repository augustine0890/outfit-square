from datetime import datetime
from typing import Tuple


def get_week_number() -> Tuple[int, int]:
    """Returns the current ISO week number as a tuple of (year, week number)."""
    current_date = datetime.now()
    year, week, _ = current_date.isocalendar()
    return year, week


def is_today_thursday() -> bool:
    """Checks if today is Thursday."""
    return datetime.now().strftime("%A") == "Thursday"
