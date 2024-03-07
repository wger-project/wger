# Standard Library
from dataclasses import dataclass

# wger
from wger.manager.models import DayNg


@dataclass
class WorkoutDay:
    day: DayNg
    iteration: int
