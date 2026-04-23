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

# Standard Library
import json
import logging
import os
from typing import TYPE_CHECKING

# Third Party
import requests


if TYPE_CHECKING:
    # wger
    from wger.nutrition.gap_analyzer import NutritionGapAnalysis
    from wger.nutrition.suggestion_engine import NutritionGapSuggestions


logger = logging.getLogger(__name__)


OPENAI_API_URL = 'https://api.openai.com/v1/responses'
DEFAULT_OPENAI_MODEL = 'gpt-4o-mini'
DEFAULT_TIMEOUT_SECONDS = 8
MAX_SUGGESTIONS_IN_PROMPT = 2


def generate_coaching_message(
    analysis: 'NutritionGapAnalysis',
    suggestions: 'NutritionGapSuggestions',
    *,
    dinner_guidance: bool = True,
) -> str | None:
    """
    Generate a short coaching summary from backend-computed nutrition data.

    This is intentionally optional. If OpenAI is not configured or the request
    fails, callers receive None and the normal analyzer result still works.
    """

    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        return None

    model = os.getenv('OPENAI_NUTRITION_MODEL', DEFAULT_OPENAI_MODEL)
    prompt = build_coaching_prompt(
        analysis,
        suggestions,
        dinner_guidance=dinner_guidance,
    )

    try:
        response = requests.post(
            os.getenv('OPENAI_API_URL', OPENAI_API_URL),
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': model,
                'instructions': _get_system_instructions(),
                'input': prompt,
                'max_output_tokens': 140,
            },
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning('Could not generate smart nutrition coaching message: %s', exc)
        return None

    try:
        return _extract_output_text(response.json())
    except ValueError as exc:
        logger.warning('Could not parse smart nutrition coaching response: %s', exc)
        return None


def build_coaching_prompt(
    analysis: 'NutritionGapAnalysis',
    suggestions: 'NutritionGapSuggestions',
    *,
    dinner_guidance: bool = True,
) -> str:
    """
    Build a tightly grounded prompt from already-computed nutrition data.
    """

    prompt_data = {
        'date_analyzed': analysis.date.isoformat(),
        'nutrients': {
            nutrient: {
                'consumed': _format_decimal(gap.consumed),
                'target': _format_decimal(gap.target),
                'gap': _format_decimal(gap.gap),
                'status': gap.status,
                'goal_source': gap.goal_source,
            }
            for nutrient, gap in analysis.gaps.items()
        },
        'missing_goals': analysis.missing_goals,
        'ingredient_suggestions': _serialize_suggestions(suggestions),
        'dinner_guidance': dinner_guidance,
    }

    return (
        'Use only the following backend-computed Smart Nutrition Gap Analyzer data. '
        'Do not calculate new nutrition facts, invent nutrients, or mention foods not listed. '
        'Some meals may already have been logged earlier today, so focus on what is still left. '
        'Write at most two practical sentences framed as dinner or next-meal guidance. '
        'Prefer wording such as "For dinner", "For your next meal", or '
        '"Based on what is still left today". Mention at most two foods, and only choose from the '
        'provided ingredient_suggestions, preferring the highest-ranked suggestions. Explain which '
        'remaining nutrients the foods help address. Avoid generic motivational phrases such as '
        '"nutrition journey", "fresh start", "you\'ve got this", or '
        '"small changes make a big difference".\n\n'
        f'{json.dumps(prompt_data, indent=2)}'
    )


def _get_system_instructions() -> str:
    """
    Return the safety and scope instructions for the coaching model.
    """

    return (
        'You are a concise fitness nutrition coach giving practical next-meal guidance. '
        'The backend system is the source of truth. Summarize only the provided remaining gaps and '
        'ingredient suggestions. Do not invent nutrition facts, medical claims, or ingredients. '
        'Keep the tone specific and meal-oriented, not broadly motivational.'
    )


def _serialize_suggestions(suggestions: 'NutritionGapSuggestions') -> dict[str, list[dict]]:
    """
    Keep the prompt small by sending only the top few backend suggestions.
    """

    return {
        nutrient: [
            {
                'ingredient_name': suggestion.ingredient_name,
                'suggested_amount_grams': _format_decimal(suggestion.suggested_amount_grams),
                'estimated_contribution': _format_decimal(suggestion.estimated_contribution),
                'remaining_gap_after_suggestion': _format_decimal(
                    suggestion.remaining_gap_after_suggestion
                ),
                'also_addresses': suggestion.also_addresses,
                'score': _format_decimal(suggestion.score),
            }
            for suggestion in nutrient_suggestions[:MAX_SUGGESTIONS_IN_PROMPT]
        ]
        for nutrient, nutrient_suggestions in suggestions.suggestions.items()
    }


def _extract_output_text(response_data: dict) -> str | None:
    """
    Extract text from the Responses API JSON shape.
    """

    if response_data.get('output_text'):
        return response_data['output_text'].strip()

    for output_item in response_data.get('output', []):
        for content_item in output_item.get('content', []):
            if content_item.get('type') == 'output_text' and content_item.get('text'):
                return content_item['text'].strip()

    return None


def _format_decimal(value) -> str | None:
    """
    Convert Decimal-like values to compact strings for prompt readability.
    """
    if value is None:
        return None
    return f"{float(value):.1f}"
