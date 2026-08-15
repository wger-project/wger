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
from wger.measurements.utils.bmi import calculate_bmi
from wger.utils.constants import TWOPLACES
from wger.utils.units import AbstractWeight


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
        return [
            DesiredRow(
                external_id=row['source_id'],
                date=row['date'],
                value=row['value'],
            )
            for row in calculate_bmi(category.user)
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
        return [
            DesiredRow(
                external_id=entry.pk,
                date=entry.date,
                value=round(entry.value / height, 2),
            )
            for entry in entries
        ]


@register
class OneRepMax(DynamicMeasurementType):
    """
    One entry per calendar day (UTC) with qualifying logs of the configured
    exercise: the highest Brzycki estimate of that day, in kg. Only sets of
    at most max_reps repetitions count, both because low-rep sets are what a
    1RM estimate is about and because the formula degrades at high counts.
    """

    DEFAULT_MAX_REPS = 5

    slug = Category.DynamicType.ONE_REP_MAX
    label = '1RM'
    params_schema = {
        'type': 'object',
        'properties': {
            'exercise_id': {'type': 'integer', 'minimum': 1},
            'max_reps': {'type': 'integer', 'minimum': 1, 'maximum': 10},
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
        max_reps = params.get('max_reps', self.DEFAULT_MAX_REPS)

        logs = WorkoutLog.objects.filter(
            user_id=category.user_id,
            exercise_id=params.get('exercise_id'),
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

        return [
            DesiredRow(
                external_id=uuid.uuid5(category.pk, day.isoformat()),
                date=date,
                value=value,
            )
            for day, (value, date) in best.items()
        ]
