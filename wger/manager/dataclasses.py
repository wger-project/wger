# Standard Library
import datetime
from dataclasses import dataclass
from decimal import Decimal

# wger
from wger.manager.models import DayNg


@dataclass
class WorkoutDayData:
    day: DayNg
    date: datetime.date
    iteration: int


@dataclass
class SetConfigData:
    weight: Decimal | int
    reps: Decimal | int
    rir: Decimal | int
    rest: Decimal | int
