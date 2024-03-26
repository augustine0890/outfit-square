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


def calculate_lotto_points(
    guessed_numbers: List[int], draw_numbers: List[int]
) -> Tuple[int, int]:
    """Calculates the number of matches and reward points based on those matches."""
    matched_points = {
        1: 400,
        2: 1000,
        3: 5000,
        4: 100000,
    }
    # Calculate matches
    matches = sum(a == b for a, b in zip(guessed_numbers, draw_numbers))
    # Calculate points based on matches
    points = matched_points.get(matches, 0)

    return matches, points
