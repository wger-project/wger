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

# Standard Library
from datetime import datetime, timezone
from decimal import Decimal

# wger
from wger.core.tests import powersync_base_test
from wger.nutrition.models import (
    IngredientWeightUnit,
    LogItem,
    Meal,
    MealItem,
    NutritionPlan,
)


# Pinned in test-nutrition-data.json (uuid field on the matching pk)
PLAN_OWNED_UUID = 'cc000000-0000-0000-0000-000000000001'  # user 'test'
PLAN_OTHER_UUID = 'cc000000-0000-0000-0000-000000000002'  # user 'admin'
MEAL_OWNED_UUID = 'aa000000-0000-0000-0000-000000000001'
MEAL_OTHER_UUID = 'aa000000-0000-0000-0000-000000000003'
MEAL_ITEM_OWNED_UUID = 'bb000000-0000-0000-0000-000000000001'
MEAL_ITEM_OTHER_UUID = 'bb000000-0000-0000-0000-000000000004'

# Pinned in test-nutrition-diary.json (linked to PLAN_OWNED)
LOG_OWNED_UUID = 'ee000000-0000-0000-0000-000000000001'

INGREDIENT_PUBLIC = 1


class NutritionPlanPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """PowerSync handlers for nutrition.NutritionPlan."""

    table = 'nutrition_nutritionplan'
    resource = NutritionPlan

    pk_owned = PLAN_OWNED_UUID

    update_payload = {
        'id': pk_owned,
        'description': 'Renamed via PowerSync',
    }

    create_payload = {
        'id': 'cc000000-0000-0000-0000-000000000099',
        'description': 'created via PowerSync',
        'creation_date': '2030-01-15',
        'start': '2030-01-15',
        'end': None,
        'only_logging': False,
        'has_goal_calories': False,
        'goal_energy': None,
        'goal_protein': None,
        'goal_carbohydrates': None,
        'goal_fat': None,
        'goal_fiber': None,
    }


class MealPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """PowerSync handlers for nutrition.Meal."""

    table = 'nutrition_meal'
    resource = Meal

    pk_owned = MEAL_OWNED_UUID

    update_payload = {
        'id': pk_owned,
        'name': 'Renamed via PowerSync',
    }

    create_payload = {
        'id': 'aa000000-0000-0000-0000-000000000099',
        'plan': PLAN_OWNED_UUID,
        'name': 'created via PowerSync',
    }

    fk_ownership = (('plan', PLAN_OTHER_UUID),)


class MealItemPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """PowerSync handlers for nutrition.MealItem."""

    table = 'nutrition_mealitem'
    resource = MealItem

    pk_owned = MEAL_ITEM_OWNED_UUID

    update_payload = {
        'id': pk_owned,
        'amount': '99',
    }

    create_payload = {
        'id': 'bb000000-0000-0000-0000-000000000099',
        'meal': MEAL_OWNED_UUID,
        'ingredient': INGREDIENT_PUBLIC,
        'amount': '50',
    }

    fk_ownership = (('meal', MEAL_OTHER_UUID),)


class LogItemPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """
    PowerSync handlers for nutrition.LogItem. The handler runs
    check_fk_ownership against (NutritionPlan, 'plan') and (Meal, 'meal').
    """

    table = 'nutrition_logitem'
    resource = LogItem

    pk_owned = LOG_OWNED_UUID

    create_payload = {
        'id': 'ee000000-0000-0000-0000-000000000099',
        'plan': PLAN_OWNED_UUID,
        'datetime': '2030-01-15T10:00:00Z',
        'ingredient': INGREDIENT_PUBLIC,
        'amount': '50',
    }
    update_payload = {
        'id': pk_owned,
        'amount': '99',
    }

    fk_ownership = (('plan', PLAN_OTHER_UUID),)

    def test_portion_date_update_clears_unit_and_preserves_context(self):
        entry = LogItem.objects.get(pk=self.pk_owned)
        entry.weight_unit = IngredientWeightUnit.objects.create(
            ingredient=entry.ingredient, name='Serving', gram=125
        )
        entry.meal_id = MEAL_OWNED_UUID
        entry.comment = 'Keep this comment'
        entry.save()
        before = LogItem.objects.values().get(pk=entry.pk)

        self.authenticate()
        response = self.push(
            'PATCH',
            {
                'id': self.pk_owned,
                'amount': '80.50',
                'weight_unit': None,
                'datetime': '2026-10-25T02:30:00+01:00',
            },
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json(), {'status': 'ok!'})
        entry.refresh_from_db()
        self.assertEqual(entry.amount, Decimal('80.50'))
        self.assertIsNone(entry.weight_unit_id)
        self.assertEqual(entry.datetime, datetime(2026, 10, 25, 1, 30, tzinfo=timezone.utc))
        after = LogItem.objects.values().get(pk=entry.pk)
        for field in before.keys() - {'amount', 'weight_unit_id', 'datetime'}:
            self.assertEqual(after[field], before[field], field)

    def test_other_user_cannot_change_portion_or_date(self):
        entry = LogItem.objects.get(pk=self.pk_owned)
        entry.weight_unit = IngredientWeightUnit.objects.create(
            ingredient=entry.ingredient, name='Serving', gram=125
        )
        entry.save()
        before = LogItem.objects.values().get(pk=entry.pk)

        self.authenticate(self.user_fail)
        response = self.push(
            'PATCH',
            {
                'id': self.pk_owned,
                'amount': '80.50',
                'weight_unit': None,
                'datetime': '2026-10-25T01:30:00Z',
            },
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json(), {'status': 'ok!'})
        self.assertEqual(LogItem.objects.values().get(pk=entry.pk), before)
