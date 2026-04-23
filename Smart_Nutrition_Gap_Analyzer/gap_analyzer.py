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
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import datetime
from dataclasses import (
    asdict,
    dataclass,
)
from decimal import Decimal
from typing import TYPE_CHECKING

# wger
from wger.nutrition.helpers import NutritionalValues


if TYPE_CHECKING:
    # wger
    from wger.nutrition.models import NutritionPlan


NUTRIENT_GOAL_FIELDS = {
    'energy': 'goal_energy',
    'protein': 'goal_protein',
    'carbohydrates': 'goal_carbohydrates',
    'fat': 'goal_fat',
    'fiber': 'goal_fiber',
}

NUTRIENT_STATUS_IN_PROGRESS = 'in_progress'
NUTRIENT_STATUS_MET = 'met'
NUTRIENT_STATUS_EXCEEDED = 'exceeded'

GOAL_SOURCE_PLAN = 'plan_goal'
GOAL_SOURCE_FALLBACK = 'fallback_estimate'
GOAL_SOURCE_DEFAULT = 'default_recommendation'

DEFAULT_NUTRIENT_TARGETS = {
    'energy': Decimal('2000'),
    'protein': Decimal('50'),
    'carbohydrates': Decimal('275'),
    'fat': Decimal('70'),
    'fiber': Decimal('30'),
}

NUTRIENT_STATUS_TOLERANCE = Decimal('0.02')


@dataclass(frozen=True)
class NutrientGap:
    """
    Gap information for one nutrient.

    A positive gap means the user is still below the configured target.
    A negative gap means the user has consumed more than the configured target.
    """

    consumed: Decimal
    target: Decimal | None
    gap: Decimal | None
    is_configured: bool
    status: str
    goal_source: str

    @property
    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class NutritionGapAnalysis:
    """
    Result object returned by the nutrition gap analyzer.
    """

    date: datetime.date
    consumed: NutritionalValues
    gaps: dict[str, NutrientGap]
    missing_goals: list[str]

    @property
    def to_dict(self):
        return {
            'date': self.date,
            'consumed': self.consumed.to_dict,
            'gaps': {key: value.to_dict for key, value in self.gaps.items()},
            'missing_goals': self.missing_goals,
        }


def analyze_nutrition_gap(
    plan: 'NutritionPlan',
    date: datetime.date | None = None,
) -> NutritionGapAnalysis:
    """
    Compare logged intake for a date against the targets configured on a plan.

    If date is omitted, today's log entries are used via NutritionPlan.get_log_entries().
    Missing plan goals are reported in missing_goals and use fallback/default targets.
    """

    analysis_date = date or datetime.date.today()
    consumed = _get_consumed_totals(plan, date=date)

    gaps = {}
    missing_goals = []

    for nutrient, goal_field in NUTRIENT_GOAL_FIELDS.items():
        consumed_value = _to_decimal(getattr(consumed, nutrient))
        target_value, goal_source = _resolve_target(plan, nutrient, goal_field)
        gap = target_value - consumed_value

        gaps[nutrient] = NutrientGap(
            consumed=consumed_value,
            target=target_value,
            gap=gap,
            is_configured=goal_source == GOAL_SOURCE_PLAN,
            status=_get_nutrient_status(gap, target_value),
            goal_source=goal_source,
        )

        if goal_source != GOAL_SOURCE_PLAN:
            missing_goals.append(nutrient)

    return NutritionGapAnalysis(
        date=analysis_date,
        consumed=consumed,
        gaps=gaps,
        missing_goals=missing_goals,
    )


def _get_consumed_totals(
    plan: 'NutritionPlan',
    date: datetime.date | None = None,
) -> NutritionalValues:
    """
    Sum nutritional values from the plan's log entries for the requested date.
    """

    consumed = NutritionalValues()
    use_metric = plan.user.userprofile.use_metric

    for log_item in plan.get_log_entries(date=date):
        consumed += log_item.get_nutritional_values(use_metric=use_metric)

    return consumed


def _to_decimal(value) -> Decimal:
    """
    Convert numbers used by nutrition models into Decimal values.
    """

    if value is None:
        return Decimal('0')

    return Decimal(str(value))


def _resolve_target(
    plan: 'NutritionPlan',
    nutrient: str,
    goal_field: str,
) -> tuple[Decimal, str]:
    """
    Resolve the target value and source for a nutrient.
    """

    plan_goal = getattr(plan, goal_field)

    if plan_goal is not None:
        return _to_decimal(plan_goal), GOAL_SOURCE_PLAN

    if nutrient == 'energy' and plan.user.userprofile.calories is not None:
        return _to_decimal(plan.user.userprofile.calories), GOAL_SOURCE_FALLBACK

    return DEFAULT_NUTRIENT_TARGETS[nutrient], GOAL_SOURCE_DEFAULT


def _get_nutrient_status(gap: Decimal, target: Decimal) -> str:
    """
    Convert a numeric gap into a simple status for downstream API/UI use.
    """

    if target > 0 and abs(gap) <= target * NUTRIENT_STATUS_TOLERANCE:
        return NUTRIENT_STATUS_MET

    if gap > 0:
        return NUTRIENT_STATUS_IN_PROGRESS

    if gap < 0:
        return NUTRIENT_STATUS_EXCEEDED

    return NUTRIENT_STATUS_MET
