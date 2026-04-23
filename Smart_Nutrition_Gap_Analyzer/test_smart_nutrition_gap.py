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
import datetime
import os
from decimal import Decimal
from unittest.mock import patch

# Django
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Third Party
import requests
from rest_framework import status

# wger
from wger.core.models import Language
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.gap_analyzer import (
    GOAL_SOURCE_DEFAULT,
    GOAL_SOURCE_FALLBACK,
    GOAL_SOURCE_PLAN,
    NUTRIENT_STATUS_EXCEEDED,
    NUTRIENT_STATUS_IN_PROGRESS,
    NUTRIENT_STATUS_MET,
    analyze_nutrition_gap,
)
from wger.nutrition.llm_coach import (
    build_coaching_prompt,
    generate_coaching_message,
)
from wger.nutrition.models import (
    Ingredient,
    LogItem,
    NutritionPlan,
)
from wger.nutrition.suggestion_engine import suggest_ingredients_for_gaps


class MockOpenAIResponse:
    def __init__(self, data, json_error=None):
        self.data = data
        self.json_error = json_error

    def raise_for_status(self):
        pass

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.data


class SmartNutritionGapTestCase(WgerTestCase):
    """
    Small demo-readiness tests for the Smart Nutrition Gap Analyzer.
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.language = Language.objects.get(short_name='en')
        self.analysis_date = datetime.date.today()

        self.protein_ingredient = self._create_ingredient(
            name='AA Smart Gap Protein',
            energy=400,
            protein=100,
        )
        self.carbohydrate_ingredient = self._create_ingredient(
            name='AA Smart Gap Oats',
            energy=400,
            protein=10,
            carbohydrates=100,
            fat=5,
            fiber=100,
        )
        self.fat_ingredient = self._create_ingredient(
            name='AA Smart Gap Avocado',
            energy=900,
            protein=1,
            carbohydrates=1,
            fat=100,
            fiber=1,
        )

    def test_gap_analyzer_uses_logged_intake_and_plan_goals(self):
        plan = self._create_plan()
        LogItem.objects.create(
            plan=plan,
            ingredient=self.protein_ingredient,
            amount=Decimal('50'),
            datetime=timezone.make_aware(
                datetime.datetime.combine(self.analysis_date, datetime.time(hour=8))
            ),
        )

        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)

        self.assertEqual(analysis.gaps['energy'].consumed, Decimal('200'))
        self.assertEqual(analysis.gaps['protein'].consumed, Decimal('50.000'))
        self.assertEqual(analysis.gaps['protein'].gap, Decimal('50.000'))
        self.assertEqual(analysis.gaps['protein'].status, NUTRIENT_STATUS_IN_PROGRESS)
        self.assertEqual(analysis.gaps['protein'].goal_source, GOAL_SOURCE_PLAN)
        self.assertEqual(analysis.missing_goals, [])

    def test_gap_analyzer_marks_met_and_exceeded_nutrients(self):
        plan = self._create_plan(
            goal_energy=100,
            goal_protein=50,
            goal_carbohydrates=0,
            goal_fat=0,
            goal_fiber=0,
        )
        LogItem.objects.create(
            plan=plan,
            ingredient=self.protein_ingredient,
            amount=Decimal('50'),
            datetime=timezone.make_aware(
                datetime.datetime.combine(self.analysis_date, datetime.time(hour=8))
            ),
        )

        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)

        self.assertEqual(analysis.gaps['protein'].status, NUTRIENT_STATUS_MET)
        self.assertEqual(analysis.gaps['energy'].status, NUTRIENT_STATUS_EXCEEDED)
        self.assertEqual(analysis.gaps['carbohydrates'].status, NUTRIENT_STATUS_MET)

    def test_gap_analyzer_treats_near_target_intake_as_met(self):
        plan = self._create_plan(goal_protein=100)
        LogItem.objects.create(
            plan=plan,
            ingredient=self.protein_ingredient,
            amount=Decimal('99'),
            datetime=timezone.make_aware(
                datetime.datetime.combine(self.analysis_date, datetime.time(hour=8))
            ),
        )

        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)

        self.assertEqual(analysis.gaps['protein'].gap, Decimal('1.000'))
        self.assertEqual(analysis.gaps['protein'].status, NUTRIENT_STATUS_MET)

    def test_gap_analyzer_handles_empty_log(self):
        plan = self._create_plan()

        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)

        self.assertEqual(analysis.gaps['energy'].consumed, Decimal('0'))
        self.assertEqual(analysis.gaps['protein'].consumed, Decimal('0'))
        self.assertEqual(analysis.gaps['fiber'].consumed, Decimal('0'))
        self.assertEqual(analysis.gaps['energy'].status, NUTRIENT_STATUS_IN_PROGRESS)
        self.assertEqual(analysis.gaps['protein'].gap, Decimal('100'))

    def test_gap_analyzer_uses_fallback_and_default_targets_for_missing_goals(self):
        self.user.userprofile.calories = 1800
        self.user.userprofile.save()
        plan = self._create_plan(goal_energy=None, goal_protein=None)

        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)

        self.assertEqual(analysis.gaps['energy'].target, Decimal('1800'))
        self.assertEqual(analysis.gaps['energy'].goal_source, GOAL_SOURCE_FALLBACK)
        self.assertEqual(analysis.gaps['protein'].target, Decimal('50'))
        self.assertEqual(analysis.gaps['protein'].goal_source, GOAL_SOURCE_DEFAULT)
        self.assertIn('energy', analysis.missing_goals)
        self.assertIn('protein', analysis.missing_goals)

    def test_suggestion_engine_groups_suggestions_by_positive_gap(self):
        plan = self._create_plan()
        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)

        suggestions = suggest_ingredients_for_gaps(
            analysis,
            max_suggestions_per_nutrient=2,
        )

        self.assertIn('protein', suggestions.suggestions)
        self.assertIn('carbohydrates', suggestions.suggestions)
        self.assertIn('fat', suggestions.suggestions)
        self.assertIn('fiber', suggestions.suggestions)
        self.assertIn('energy', suggestions.suggestions)

        protein_suggestion = suggestions.suggestions['protein'][0]
        fat_suggestion = suggestions.suggestions['fat'][0]

        self.assertEqual(protein_suggestion.ingredient_name, self.protein_ingredient.name)
        self.assertEqual(fat_suggestion.ingredient_name, self.fat_ingredient.name)
        self.assertEqual(fat_suggestion.serving_min_grams, Decimal('10.00'))
        self.assertEqual(fat_suggestion.serving_max_grams, Decimal('30.00'))
        self.assertIn('energy', protein_suggestion.also_addresses)

    def test_suggestion_engine_penalizes_side_effects_for_met_or_exceeded_nutrients(self):
        clean_protein = self._create_ingredient(
            name='AA Smart Gap Clean Protein',
            energy=80,
            protein=80,
        )
        heavy_protein = self._create_ingredient(
            name='AA Smart Gap Heavy Protein',
            energy=900,
            protein=100,
            fat=100,
        )
        plan = self._create_plan(
            goal_energy=100,
            goal_protein=100,
            goal_carbohydrates=0,
            goal_fat=0,
            goal_fiber=0,
        )
        LogItem.objects.create(
            plan=plan,
            ingredient=self.fat_ingredient,
            amount=Decimal('20'),
            datetime=timezone.make_aware(
                datetime.datetime.combine(self.analysis_date, datetime.time(hour=8))
            ),
        )

        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)
        suggestions = suggest_ingredients_for_gaps(
            analysis,
            max_suggestions_per_nutrient=5,
        )
        protein_suggestions = suggestions.suggestions['protein']
        clean_suggestion = next(
            suggestion
            for suggestion in protein_suggestions
            if suggestion.ingredient_id == clean_protein.id
        )
        heavy_suggestion = next(
            suggestion
            for suggestion in protein_suggestions
            if suggestion.ingredient_id == heavy_protein.id
        )

        self.assertEqual(protein_suggestions[0].ingredient_id, clean_protein.id)
        self.assertLess(heavy_suggestion.score, clean_suggestion.score)
        self.assertGreater(heavy_suggestion.side_effect_penalty, Decimal('0'))
        self.assertIn('energy', heavy_suggestion.penalized_nutrients)
        self.assertIn('fat', heavy_suggestion.penalized_nutrients)

    def test_llm_coach_builds_grounded_prompt_from_backend_data(self):
        plan = self._create_plan()
        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)
        suggestions = suggest_ingredients_for_gaps(
            analysis,
            max_suggestions_per_nutrient=2,
        )

        prompt = build_coaching_prompt(analysis, suggestions)

        self.assertIn('backend-computed Smart Nutrition Gap Analyzer data', prompt)
        self.assertIn('"protein"', prompt)
        self.assertIn(self.protein_ingredient.name, prompt)
        self.assertIn('Do not calculate new nutrition facts', prompt)

    @patch.dict(os.environ, {'OPENAI_API_KEY': ''})
    def test_llm_coach_returns_none_without_api_key(self):
        plan = self._create_plan()
        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)
        suggestions = suggest_ingredients_for_gaps(analysis)

        message = generate_coaching_message(analysis, suggestions)

        self.assertIsNone(message)

    @patch.dict(
        os.environ,
        {
            'OPENAI_API_KEY': 'test-key',
            'OPENAI_NUTRITION_MODEL': 'gpt-test-model',
        },
    )
    @patch('wger.nutrition.llm_coach.requests.post')
    def test_llm_coach_returns_openai_message(self, mock_post):
        mock_post.return_value = MockOpenAIResponse(
            {
                'output': [
                    {
                        'content': [
                            {
                                'type': 'output_text',
                                'text': 'You still have some protein left for today.',
                            }
                        ]
                    }
                ]
            }
        )
        plan = self._create_plan()
        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)
        suggestions = suggest_ingredients_for_gaps(analysis)

        message = generate_coaching_message(analysis, suggestions)

        self.assertEqual(message, 'You still have some protein left for today.')
        mock_post.assert_called_once()
        self.assertEqual(mock_post.call_args.kwargs['json']['model'], 'gpt-test-model')

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('wger.nutrition.llm_coach.requests.post')
    def test_llm_coach_returns_none_for_invalid_openai_json(self, mock_post):
        mock_post.return_value = MockOpenAIResponse({}, json_error=ValueError('bad json'))
        plan = self._create_plan()
        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)
        suggestions = suggest_ingredients_for_gaps(analysis)

        message = generate_coaching_message(analysis, suggestions)

        self.assertIsNone(message)

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('wger.nutrition.llm_coach.requests.post')
    def test_llm_coach_returns_none_when_openai_request_fails(self, mock_post):
        mock_post.side_effect = requests.Timeout('request timed out')
        plan = self._create_plan()
        analysis = analyze_nutrition_gap(plan, date=self.analysis_date)
        suggestions = suggest_ingredients_for_gaps(analysis)

        message = generate_coaching_message(analysis, suggestions)

        self.assertIsNone(message)

    def test_api_endpoint_returns_gap_analysis_and_suggestions(self):
        self.user_login('admin')
        plan = self._create_plan()

        response = self.client.get(
            f'/api/v2/nutritionplan/{plan.id}/smart-nutrition-gap/',
            {'date': self.analysis_date.isoformat(), 'max_suggestions': 2},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan_id'], plan.id)
        self.assertEqual(response.data['date_analyzed'], self.analysis_date)
        self.assertIn('protein', response.data['consumed_totals'])
        self.assertIn('protein', response.data['nutrient_gaps'])
        self.assertEqual(
            response.data['nutrient_statuses']['protein'],
            NUTRIENT_STATUS_IN_PROGRESS,
        )
        self.assertEqual(response.data['goal_sources']['protein'], GOAL_SOURCE_PLAN)
        self.assertIn('protein', response.data['ingredient_suggestions'])
        self.assertIn('also_addresses', response.data['ingredient_suggestions']['protein'][0])
        self.assertIn(
            'side_effect_penalty',
            response.data['ingredient_suggestions']['protein'][0],
        )

    @patch('wger.nutrition.api.views.generate_coaching_message')
    def test_api_endpoint_optionally_returns_coaching_message(self, mock_coach):
        mock_coach.return_value = 'A short coaching summary.'
        self.user_login('admin')
        plan = self._create_plan()

        response = self.client.get(
            f'/api/v2/nutritionplan/{plan.id}/smart-nutrition-gap/',
            {'include_coaching': 'true'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['coaching_message'], 'A short coaching summary.')
        mock_coach.assert_called_once()

    @patch.dict(os.environ, {'OPENAI_API_KEY': ''})
    def test_api_endpoint_with_coaching_enabled_handles_missing_api_key(self):
        self.user_login('admin')
        plan = self._create_plan()

        response = self.client.get(
            f'/api/v2/nutritionplan/{plan.id}/smart-nutrition-gap/',
            {'include_coaching': 'true'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['coaching_message'])
        self.assertIn('nutrient_gaps', response.data)
        self.assertIn('ingredient_suggestions', response.data)

    def test_api_endpoint_does_not_expose_another_users_plan(self):
        plan = self._create_plan()
        self.user_login('test')

        response = self.client.get(f'/api/v2/nutritionplan/{plan.id}/smart-nutrition-gap/')

        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )

    def test_standalone_page_renders_gap_analysis(self):
        self.user_login('admin')
        plan = self._create_plan()

        response = self.client.get(
            reverse('nutrition:plan:smart-nutrition-gap', kwargs={'pk': plan.id}),
            {'date': self.analysis_date.isoformat()},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Smart nutrition gap analyzer')
        self.assertContains(response, 'Nutrient progress')
        self.assertContains(response, 'Ingredient suggestions')
        self.assertContains(response, self.protein_ingredient.name)

    @patch('wger.nutrition.llm_coach.generate_coaching_message')
    def test_standalone_page_renders_optional_coaching_message(self, mock_coach):
        mock_coach.return_value = 'A short coaching summary.'
        self.user_login('admin')
        plan = self._create_plan()

        response = self.client.get(
            reverse('nutrition:plan:smart-nutrition-gap', kwargs={'pk': plan.id}),
            {'date': self.analysis_date.isoformat()},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Coaching summary')
        self.assertContains(response, 'A short coaching summary.')

    @patch('wger.nutrition.llm_coach.generate_coaching_message')
    def test_standalone_page_still_renders_when_coaching_fails(self, mock_coach):
        mock_coach.side_effect = RuntimeError('LLM unavailable')
        self.user_login('admin')
        plan = self._create_plan()

        response = self.client.get(
            reverse('nutrition:plan:smart-nutrition-gap', kwargs={'pk': plan.id}),
            {'date': self.analysis_date.isoformat()},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Nutrient progress')
        self.assertContains(response, 'Ingredient suggestions')
        self.assertNotContains(response, 'Coaching summary')

    def _create_plan(self, **overrides):
        data = {
            'user': self.user,
            'description': 'Smart Nutrition Gap Demo',
            'goal_energy': 500,
            'goal_protein': 100,
            'goal_carbohydrates': 100,
            'goal_fat': 50,
            'goal_fiber': 30,
        }
        data.update(overrides)
        return NutritionPlan.objects.create(**data)

    def _create_ingredient(
        self,
        *,
        name,
        energy=0,
        protein=0,
        carbohydrates=0,
        fat=0,
        fiber=0,
    ):
        return Ingredient.objects.create(
            language=self.language,
            name=name,
            energy=energy,
            protein=Decimal(str(protein)),
            carbohydrates=Decimal(str(carbohydrates)),
            fat=Decimal(str(fat)),
            fiber=Decimal(str(fiber)),
            license_id=2,
            license_author='wger test',
        )
