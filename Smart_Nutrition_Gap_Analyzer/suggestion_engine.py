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
from dataclasses import (
    asdict,
    dataclass,
)
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)
from typing import TYPE_CHECKING

# wger
from wger.nutrition.gap_analyzer import (
    NUTRIENT_STATUS_EXCEEDED,
    NUTRIENT_STATUS_IN_PROGRESS,
    NUTRIENT_STATUS_MET,
)
from wger.nutrition.models import Ingredient


if TYPE_CHECKING:
    # wger
    from wger.nutrition.gap_analyzer import (
        NutrientGap,
        NutritionGapAnalysis,
    )


SUGGESTED_NUTRIENTS = (
    'protein',
    'carbohydrates',
    'fat',
    'fiber',
    'energy',
)

DEFAULT_MAX_SUGGESTIONS_PER_NUTRIENT = 5
DEFAULT_CANDIDATE_POOL_SIZE = 50
SIDE_EFFECT_PENALTY_WEIGHT = Decimal('0.25')
MAX_SIDE_EFFECT_PENALTY = Decimal('0.75')

SERVING_RANGES_GRAMS = {
    'protein': (Decimal('30'), Decimal('200')),
    'carbohydrates': (Decimal('40'), Decimal('200')),
    'fat': (Decimal('10'), Decimal('30')),
    'fiber': (Decimal('30'), Decimal('150')),
    'energy': (Decimal('30'), Decimal('200')),
}


@dataclass(frozen=True)
class IngredientSuggestion:
    """
    A rule-based ingredient suggestion for one nutrient gap.
    """

    ingredient_id: int
    ingredient_name: str
    nutrient: str
    nutrient_per_100g: Decimal
    gap: Decimal
    suggested_amount_grams: Decimal
    estimated_contribution: Decimal
    remaining_gap_after_suggestion: Decimal
    score: Decimal
    side_effect_penalty: Decimal
    serving_min_grams: Decimal
    serving_max_grams: Decimal
    also_addresses: list[str]
    penalized_nutrients: list[str]

    @property
    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class NutritionGapSuggestions:
    """
    Result object returned by the suggestion engine.
    """

    suggestions: dict[str, list[IngredientSuggestion]]
    nutrient_statuses: dict[str, str]
    skipped_nutrients: list[str]

    @property
    def to_dict(self):
        return {
            'suggestions': {
                nutrient: [suggestion.to_dict for suggestion in nutrient_suggestions]
                for nutrient, nutrient_suggestions in self.suggestions.items()
            },
            'nutrient_statuses': self.nutrient_statuses,
            'skipped_nutrients': self.skipped_nutrients,
        }


def suggest_ingredients_for_gaps(
    analysis: 'NutritionGapAnalysis',
    *,
    max_suggestions_per_nutrient: int = DEFAULT_MAX_SUGGESTIONS_PER_NUTRIENT,
    candidate_pool_size: int = DEFAULT_CANDIDATE_POOL_SIZE,
) -> NutritionGapSuggestions:
    """
    Suggest ingredients that can help close positive nutrient gaps.

    This is intentionally rule-based: for each configured positive gap, it finds
    ingredients with a positive value for that nutrient and ranks them by the
    amount of the target nutrient available per 100g, then applies a small
    penalty when the ingredient adds nutrients that are already met or exceeded.
    """

    suggestions: dict[str, list[IngredientSuggestion]] = {}
    nutrient_statuses = {}
    skipped_nutrients = []
    positive_gaps = _get_positive_gaps(analysis)

    for nutrient in SUGGESTED_NUTRIENTS:
        nutrient_gap = analysis.gaps.get(nutrient)
        nutrient_statuses[nutrient] = nutrient_gap.status if nutrient_gap else 'met'

        if not nutrient_gap:
            skipped_nutrients.append(nutrient)
            continue

        if (
            nutrient_gap.status != NUTRIENT_STATUS_IN_PROGRESS
            or nutrient_gap.gap is None
            or nutrient_gap.gap <= 0
        ):
            skipped_nutrients.append(nutrient)
            continue

        suggestions[nutrient] = _suggest_for_nutrient(
            nutrient=nutrient,
            gap=nutrient_gap.gap,
            nutrient_gaps=analysis.gaps,
            positive_gaps=positive_gaps,
            max_suggestions=max_suggestions_per_nutrient,
            candidate_pool_size=candidate_pool_size,
        )

    return NutritionGapSuggestions(
        suggestions=suggestions,
        nutrient_statuses=nutrient_statuses,
        skipped_nutrients=skipped_nutrients,
    )


def _suggest_for_nutrient(
    *,
    nutrient: str,
    gap: Decimal,
    nutrient_gaps: dict[str, 'NutrientGap'],
    positive_gaps: dict[str, Decimal],
    max_suggestions: int,
    candidate_pool_size: int,
) -> list[IngredientSuggestion]:
    """
    Return ranked suggestions for a single nutrient.
    """

    ingredients = (
        Ingredient.objects.filter(**{f'{nutrient}__gt': 0})
        .only(
            'id',
            'name',
            'energy',
            'protein',
            'carbohydrates',
            'fat',
            'fiber',
        )
        .order_by(f'-{nutrient}', 'name')[:candidate_pool_size]
    )

    suggestions = [
        _build_suggestion(
            ingredient=ingredient,
            nutrient=nutrient,
            gap=gap,
            nutrient_gaps=nutrient_gaps,
            positive_gaps=positive_gaps,
        )
        for ingredient in ingredients
    ]

    suggestions.sort(key=lambda suggestion: suggestion.score, reverse=True)
    return suggestions[:max_suggestions]


def _build_suggestion(
    *,
    ingredient: Ingredient,
    nutrient: str,
    gap: Decimal,
    nutrient_gaps: dict[str, 'NutrientGap'],
    positive_gaps: dict[str, Decimal],
) -> IngredientSuggestion:
    """
    Build a suggestion for one ingredient and one positive nutrient gap.
    """

    nutrient_per_100g = _to_decimal(getattr(ingredient, nutrient))
    serving_min, serving_max = SERVING_RANGES_GRAMS[nutrient]
    exact_amount = gap / nutrient_per_100g * Decimal('100')
    suggested_amount = _clamp(exact_amount, serving_min, serving_max)
    contribution = nutrient_per_100g * suggested_amount / Decimal('100')
    remaining_gap = gap - contribution
    base_score = min(contribution, gap) / gap
    side_effect_penalty, penalized_nutrients = _get_side_effect_penalty(
        ingredient=ingredient,
        target_nutrient=nutrient,
        suggested_amount=suggested_amount,
        nutrient_gaps=nutrient_gaps,
    )
    score = max(base_score - side_effect_penalty, Decimal('0'))

    return IngredientSuggestion(
        ingredient_id=ingredient.id,
        ingredient_name=ingredient.name,
        nutrient=nutrient,
        nutrient_per_100g=_round(nutrient_per_100g),
        gap=_round(gap),
        suggested_amount_grams=_round(suggested_amount),
        estimated_contribution=_round(contribution),
        remaining_gap_after_suggestion=_round(max(remaining_gap, Decimal('0'))),
        score=_round(score),
        side_effect_penalty=_round(side_effect_penalty),
        serving_min_grams=_round(serving_min),
        serving_max_grams=_round(serving_max),
        also_addresses=_get_also_addressed_nutrients(
            ingredient=ingredient,
            target_nutrient=nutrient,
            positive_gaps=positive_gaps,
        ),
        penalized_nutrients=penalized_nutrients,
    )


def _get_positive_gaps(analysis: 'NutritionGapAnalysis') -> dict[str, Decimal]:
    """
    Return positive in-progress gaps that can be used for suggestions.
    """

    return {
        nutrient: nutrient_gap.gap
        for nutrient, nutrient_gap in analysis.gaps.items()
        if nutrient in SUGGESTED_NUTRIENTS
        and nutrient_gap.status == NUTRIENT_STATUS_IN_PROGRESS
        and nutrient_gap.gap is not None
        and nutrient_gap.gap > 0
    }


def _get_also_addressed_nutrients(
    *,
    ingredient: Ingredient,
    target_nutrient: str,
    positive_gaps: dict[str, Decimal],
) -> list[str]:
    """
    Return other positive gaps this ingredient can also help address.
    """

    return [
        nutrient
        for nutrient in SUGGESTED_NUTRIENTS
        if nutrient != target_nutrient
        and nutrient in positive_gaps
        and _to_decimal(getattr(ingredient, nutrient)) > 0
    ]


def _get_side_effect_penalty(
    *,
    ingredient: Ingredient,
    target_nutrient: str,
    suggested_amount: Decimal,
    nutrient_gaps: dict[str, 'NutrientGap'],
) -> tuple[Decimal, list[str]]:
    """
    Penalize suggestions that add nutrients the user has already met or exceeded.
    """

    penalty = Decimal('0')
    penalized_nutrients = []

    for nutrient in SUGGESTED_NUTRIENTS:
        if nutrient == target_nutrient:
            continue

        nutrient_gap = nutrient_gaps.get(nutrient)
        if not nutrient_gap or nutrient_gap.status not in (
            NUTRIENT_STATUS_MET,
            NUTRIENT_STATUS_EXCEEDED,
        ):
            continue

        contribution = _to_decimal(getattr(ingredient, nutrient)) * suggested_amount / Decimal(
            '100'
        )

        if contribution <= 0:
            continue

        reference_value = max(
            _to_decimal(nutrient_gap.target),
            _to_decimal(nutrient_gap.consumed),
            Decimal('1'),
        )
        penalty += min(contribution / reference_value, Decimal('1')) * SIDE_EFFECT_PENALTY_WEIGHT
        penalized_nutrients.append(nutrient)

    return min(penalty, MAX_SIDE_EFFECT_PENALTY), penalized_nutrients


def _clamp(value: Decimal, minimum: Decimal, maximum: Decimal) -> Decimal:
    """
    Keep a suggested serving inside the nutrient-specific serving range.
    """

    return max(minimum, min(value, maximum))


def _to_decimal(value) -> Decimal:
    """
    Convert model numbers into Decimal values for predictable calculations.
    """

    if value is None:
        return Decimal('0')

    return Decimal(str(value))


def _round(value: Decimal) -> Decimal:
    """
    Round user-facing suggestion values to two decimal places.
    """

    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
