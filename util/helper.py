import random
from datetime import datetime
from typing import Tuple, List


def get_week_number() -> Tuple[int, int]:
    """Returns the current ISO week number as a tuple of (year, week number)."""
    current_date = datetime.now()
    year, week, _ = current_date.isocalendar()
    return year, week


def is_today_thursday() -> bool:
    """Checks if today is Thursday."""
    return datetime.now().strftime("%A") == "Thursday"


def lotto_drawing() -> List[int]:
    """Returns a list of 4 random numbers between 0 and 9"""
    return [random.randint(0, 9) for _ in range(0, 4)]
