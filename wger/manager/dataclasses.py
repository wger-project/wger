#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Standard Library
import datetime
from collections import defaultdict
from dataclasses import (
    dataclass,
    field,
)
from decimal import (
    ROUND_DOWN,
    Decimal,
)
from typing import (
    Any,
    List,
)

# Django
from django.utils.translation import gettext as _

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.utils.helpers import normalize_decimal


@dataclass
class SetConfigData:
    exercise: int

    weight: Decimal | int | None
    reps: Decimal | int | None
    rir: Decimal | int | None
    rest: int | None

    max_weight: Decimal | int | None = None
    max_reps: Decimal | int | None = None
    max_rest: int | None = None
    max_sets: int | None = None

    sets: int = 1
    weight_unit: int | None = 1
    reps_unit: int | None = 1
    weight_rounding: Decimal | int | None = 1.25
    reps_rounding: Decimal | int | None = 1

    comment: str = ''
    type: str = 'normal'
    slot_entry_id: int | None = None

    @property
    def rpe(self):
        """Converts the RiR scale to RPE"""

        if not self.rir:
            return None

        # If the RiR is too high, just approximate to 4
        if self.rir > 5:
            return 4

        return 10 - self.rir

    @property
    def text_repr(self) -> str:
        """
        Smart text representation of the set

        This converts the values to something readable like "10 × 100 kg @ 2.00RiR"
        """

        out = []

        if self.sets and self.sets > 1:
            sets = self.sets
            if self.max_sets:
                sets = f'{sets}-{self.max_sets}'

            out.append(f'{sets} {_("Sets")},')

        if self.reps:
            reps = round_value(self.reps, self.reps_rounding)
            max_reps = (
                round_value(self.max_reps, self.reps_rounding) if self.max_reps else self.max_reps
            )

            if max_reps:
                reps = f'{reps}-{max_reps}'

            unit = ''
            if self.reps_unit in (1, 2) and not self.weight:
                unit = _('Reps')
            elif self.reps_unit == 2:
                unit = '∞'
                reps = ''
            elif self.reps_unit not in (1, 2):
                unit = _(RepetitionUnit.objects.get(pk=self.reps_unit).name)

            out.append(f'{reps} {unit}'.strip())

            if self.weight:
                out.append('×')

        if self.weight:
            weight = round_value(self.weight, self.weight_rounding)
            max_weight = (
                round_value(self.max_weight, self.weight_rounding)
                if self.max_weight
                else self.max_weight
            )

            if max_weight:
                weight = f'{weight}-{max_weight}'

            unit = ''
            if self.weight_unit:
                unit = _(WeightUnit.objects.get(pk=self.weight_unit).name)

            out.append(f'{weight} {unit}'.strip())

        if self.rir:
            rir = round_value(self.rir, 0.5)
            out.append(f'@ {rir} {_("RiR")}')

        if self.rest:
            rest = self.rest
            if self.max_rest:
                rest = f'{rest}-{self.max_rest}'

            out.append(f'{rest}s {_("rest")}')

        return ' '.join(out).strip(',')


@dataclass
class SetExerciseData:
    config: Any  # 'SlotEntry'
    data: SetConfigData

    @property
    def exercise(self):
        return self.config.exercise


@dataclass
class SlotData:
    comment: str
    exercises: List[int] = field(default_factory=list)
    sets: List[SetConfigData] = field(default_factory=list)

    @property
    def is_superset(self) -> bool:
        return len(self.exercises) > 1


@dataclass
class WorkoutDayData:
    day: Any  # 'Day'
    date: datetime.date
    iteration: int | None
    label: str | None = None

    @property
    def slots_gym_mode(self) -> List[SlotData]:
        if not self.day:
            return []

        return self.day.get_slots_gym_mode(self.iteration)

    @property
    def slots_display_mode(self) -> List[SlotData]:
        """Returns the slots optimized for display in the template"""

        if not self.day:
            return []

        return self.day.get_slots_display_mode(self.iteration)


@dataclass
class LogData:
    exercises: defaultdict[int, Decimal] = field(default_factory=lambda: defaultdict(Decimal))
    muscle: defaultdict[int, Decimal] = field(default_factory=lambda: defaultdict(Decimal))
    upper_body: Decimal = 0
    lower_body: Decimal = 0
    total: Decimal = 0


@dataclass
class GroupedLogData:
    mesocycle: LogData = field(default_factory=LogData)
    iteration: defaultdict[int, LogData] = field(default_factory=lambda: defaultdict(LogData))
    weekly: defaultdict[int, LogData] = field(default_factory=lambda: defaultdict(LogData))
    daily: defaultdict[datetime.date, LogData] = field(default_factory=lambda: defaultdict(LogData))


@dataclass
class RoutineLogData:
    volume: GroupedLogData = field(default_factory=GroupedLogData)
    intensity: GroupedLogData = field(default_factory=GroupedLogData)
    sets: GroupedLogData = field(default_factory=GroupedLogData)


def round_value(
    x: int | float | Decimal | None,
    base: int | float | Decimal | None = None,
) -> Decimal | None:
    """
    Rounds a value to the nearest base

    If the base is None, the value will be returned as a Decimal object.
    """
    if x is None:
        return x

    # If the result is an integer, remove the decimal part
    result = Decimal(x) if base is None else Decimal(base * round(Decimal(x) / Decimal(base)))
    if result == result.to_integral_value():
        result = result.quantize(1, ROUND_DOWN)

    return result
