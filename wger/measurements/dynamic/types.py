# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import datetime
import uuid
from decimal import Decimal

# Django
from django.core.exceptions import ValidationError as DjangoValidationError

# wger
from wger.core.models import UserProfile
from wger.exercises.models import Exercise
from wger.manager.consts import (
    REP_UNIT_REPETITIONS,
    WEIGHT_UNIT_KG,
    WEIGHT_UNIT_LB,
)
from wger.manager.helpers import brzycki_one_rm
from wger.manager.models import WorkoutLog
from wger.measurements.dynamic.base import (
    Dependency,
    DesiredRow,
    DynamicMeasurementType,
    register,
)
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType
from wger.measurements.models.measurement import MeasurementSource
from wger.utils.constants import TWOPLACES
from wger.utils.units import (
    AbstractHeight,
    AbstractWeight,
)


# The units a length may be written in, and what a value in one of them has to
# be multiplied with to become centimeters. Mirrored in the clients, e.g.
# LENGTH_UNITS in react's models/Calculation.ts
LENGTH_UNITS = {
    'mm': Decimal('0.1'),
    'millimeter': Decimal('0.1'),
    'millimeters': Decimal('0.1'),
    'cm': Decimal(1),
    'centimeter': Decimal(1),
    'centimeters': Decimal(1),
    'm': Decimal(100),
    'meter': Decimal(100),
    'meters': Decimal(100),
    'in': AbstractHeight.INCHES_IN_CM,
    'inch': AbstractHeight.INCHES_IN_CM,
    'inches': AbstractHeight.INCHES_IN_CM,
    '"': AbstractHeight.INCHES_IN_CM,
    '″': AbstractHeight.INCHES_IN_CM,
}


@register
class Bmi(DynamicMeasurementType):
    """
    One BMI entry per body weight entry, from the official body weight
    category and the height of the profile
    """

    slug = Category.DynamicType.BMI
    label = 'BMI'
    params_schema = {'type': 'object', 'additionalProperties': False}
    depends_on = [
        Dependency(
            Measurement,
            user_id=lambda entry: entry.category.user_id,
            when=lambda entry: entry.category.metric_type == MetricType.BODY_WEIGHT,
        ),
        # The height lives on the profile
        Dependency(UserProfile, user_id=lambda profile: profile.user_id),
    ]

    def compute(self, category: Category) -> list[DesiredRow]:
        profile = category.user.userprofile
        if not profile.height or profile.height <= 0:
            return []

        # The profile height is centimeters, the formula wants meters
        height_sq = (Decimal(profile.height) / 100) ** 2

        # Calculated entries are never an input, otherwise a body weight
        # category calculating itself would grow with every run
        entries = Measurement.body_weight_for(category.user).exclude(
            source=MeasurementSource.CALCULATED
        )

        return [
            DesiredRow(
                external_id=entry.pk,
                date=entry.date,
                value=round(entry.value_in('kg') / height_sq, 2),
            )
            for entry in entries
        ]


@register
class WaistToHeightRatio(DynamicMeasurementType):
    """
    One ratio entry per entry of the configured source category, divided by
    the height of the profile. Both are read as centimeters.
    """

    slug = Category.DynamicType.WHTR
    label = 'Waist-to-height ratio'
    params_schema = {
        'type': 'object',
        'properties': {'category_id': {'type': 'string'}},
        'required': ['category_id'],
        'additionalProperties': False,
    }
    depends_on = [
        Dependency(Measurement, user_id=lambda entry: entry.category.user_id),
        Dependency(UserProfile, user_id=lambda profile: profile.user_id),
    ]

    def validate_params(self, user_id, params):
        source = self._source_category(user_id, params)
        if source is None:
            raise ValueError('The source category does not exist')
        if source.dynamic_type != Category.DynamicType.NONE:
            raise ValueError('A calculated category cannot be the source of another one')
        if self._cm_factor(source.unit) is None:
            raise ValueError('The source category has to be measured in a length unit')

    @staticmethod
    def _cm_factor(unit: str) -> Decimal | None:
        """
        What a value of this unit has to be multiplied with to become
        centimeters, or None if it is not a length this type understands.
        """
        return LENGTH_UNITS.get((unit or '').strip().lower().rstrip('.'))

    @staticmethod
    def _source_category(user_id, params) -> Category | None:
        """
        The category the ratio reads from; the user filter is the ownership
        boundary
        """
        try:
            return Category.objects.get(pk=params.get('category_id'), user_id=user_id)
        except (Category.DoesNotExist, DjangoValidationError, ValueError, TypeError):
            return None

    def compute(self, category: Category) -> list[DesiredRow]:
        profile = category.user.userprofile
        if not profile.height or profile.height <= 0:
            return []

        source = self._source_category(category.user_id, category.dynamic_params)
        if source is None or source.pk == category.pk:
            return []

        height = Decimal(profile.height)
        entries = Measurement.objects.filter(category=source).exclude(
            source=MeasurementSource.CALCULATED
        )

        rows = []
        for entry in entries:
            # An entry can carry a unit of its own, and a value whose unit
            # this type cannot read would produce a plausible wrong ratio
            factor = self._cm_factor(entry.unit)
            if factor is None:
                continue
            rows.append(
                DesiredRow(
                    external_id=entry.pk,
                    date=entry.date,
                    value=round(entry.value * factor / height, 2),
                )
            )
        return rows


DEFAULT_MAX_REPS = 5
DEFAULT_WINDOW_DAYS = 30

MAX_REPS_SCHEMA = {'type': 'integer', 'minimum': 1, 'maximum': 10}


def daily_best_estimates(user_id: int, exercise_id, max_reps) -> dict:
    """
    Per calendar day (UTC) the best Brzycki estimate among the qualifying
    sets of the exercise, as day -> (value in kg, datetime of the set).

    Qualifying means: 1 to max_reps repetitions counted in repetitions, a
    weight over zero in kg or lb. The rep cap exists both because low-rep
    sets are what a 1RM estimate is about and because the formula degrades
    at high counts.
    """
    logs = WorkoutLog.objects.filter(
        user_id=user_id,
        exercise_id=exercise_id,
        repetitions__gte=1,
        repetitions__lte=max_reps,
        repetitions_unit_id=REP_UNIT_REPETITIONS,
        weight__gt=0,
        weight_unit_id__in=(WEIGHT_UNIT_KG, WEIGHT_UNIT_LB),
    )

    # Per day the set with the highest estimate; the datetime breaks ties
    best = {}
    for log in logs:
        weight = (
            log.weight
            if log.weight_unit_id == WEIGHT_UNIT_KG
            else AbstractWeight(log.weight, 'lb').kg
        )
        one_rm = brzycki_one_rm(weight, log.repetitions).quantize(TWOPLACES)
        day = log.date.date()
        if day not in best or (one_rm, log.date) > best[day]:
            best[day] = (one_rm, log.date)
    return best


@register
class OneRepMax(DynamicMeasurementType):
    """
    One entry per calendar day (UTC) with qualifying logs of the configured
    exercise: the highest Brzycki estimate of that day, in kg
    """

    slug = Category.DynamicType.ONE_REP_MAX
    label = '1RM'
    params_schema = {
        'type': 'object',
        'properties': {
            'exercise_id': {'type': 'integer', 'minimum': 1},
            'max_reps': MAX_REPS_SCHEMA,
        },
        'required': ['exercise_id'],
        'additionalProperties': False,
    }
    depends_on = [
        Dependency(WorkoutLog, user_id=lambda log: log.user_id),
    ]

    def validate_params(self, user_id, params):
        if not Exercise.objects.filter(pk=params.get('exercise_id')).exists():
            raise ValueError('The exercise does not exist')

    def compute(self, category: Category) -> list[DesiredRow]:
        params = category.dynamic_params
        best = daily_best_estimates(
            category.user_id,
            params.get('exercise_id'),
            params.get('max_reps', DEFAULT_MAX_REPS),
        )

        return [
            DesiredRow(
                external_id=uuid.uuid5(category.pk, day.isoformat()),
                date=date,
                value=value,
            )
            for day, (value, date) in best.items()
        ]


@register
class OneRmTotal(DynamicMeasurementType):
    """
    One entry per day any of the configured exercises was trained: the sum
    of the exercises' best estimates in the rolling window ending that day,
    in kg. The window says "what you can lift right now", so a lift whose
    last heavy set expired lowers the total at the next training day.

    A day only gets an entry when every exercise has a qualifying set in
    its window, a partial total would read as a drop.
    """

    slug = Category.DynamicType.ONE_RM_TOTAL
    label = '1RM total'
    params_schema = {
        'type': 'object',
        'properties': {
            'exercise_ids': {
                'type': 'array',
                'items': {'type': 'integer', 'minimum': 1},
                'minItems': 2,
                'maxItems': 5,
                'uniqueItems': True,
            },
            'max_reps': MAX_REPS_SCHEMA,
            'window_days': {'type': 'integer', 'minimum': 7, 'maximum': 120},
        },
        'required': ['exercise_ids'],
        'additionalProperties': False,
    }
    depends_on = [
        Dependency(WorkoutLog, user_id=lambda log: log.user_id),
    ]

    def validate_params(self, user_id, params):
        exercise_ids = params.get('exercise_ids') or []
        found = Exercise.objects.filter(pk__in=exercise_ids).count()
        if found != len(exercise_ids):
            raise ValueError('One or more of the exercises do not exist')

    def compute(self, category: Category) -> list[DesiredRow]:
        params = category.dynamic_params
        max_reps = params.get('max_reps', DEFAULT_MAX_REPS)
        window = datetime.timedelta(days=params.get('window_days', DEFAULT_WINDOW_DAYS))

        per_exercise = [
            daily_best_estimates(category.user_id, exercise_id, max_reps)
            for exercise_id in params.get('exercise_ids', [])
        ]
        if not per_exercise:
            return []

        rows = []
        training_days = sorted(set().union(*(days.keys() for days in per_exercise)))
        for day in training_days:
            floor = day - window

            total = Decimal(0)
            for days in per_exercise:
                in_window = [entry for d, entry in days.items() if floor < d <= day]
                if not in_window:
                    total = None
                    break
                total += max(in_window)[0]
            if total is None:
                continue

            # The entry sits at the set that produced the day's point
            row_datetime = max(days[day][1] for days in per_exercise if day in days)
            rows.append(
                DesiredRow(
                    external_id=uuid.uuid5(category.pk, day.isoformat()),
                    date=row_datetime,
                    value=total,
                )
            )
        return rows
