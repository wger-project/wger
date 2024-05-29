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
import logging
from decimal import Decimal

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition import models
from wger.utils.constants import TWOPLACES


logger = logging.getLogger(__name__)


class NutritionalValuesCalculationsTestCase(WgerTestCase):
    """
    Tests the nutritional values calculators in the different models
    """

    def test_calculations(self):
        plan = models.NutritionPlan(user_id=1)
        plan.save()

        meal = models.Meal(order=1)
        meal.plan = plan
        meal.save()

        ingredient = models.Ingredient.objects.get(pk=1)
        ingredient2 = models.Ingredient.objects.get(pk=2)
        ingredient3 = models.Ingredient.objects.get(pk=2)

        # One ingredient, 100 gr
        item = models.MealItem()
        item.meal = meal
        item.ingredient = ingredient
        item.weight_unit_id = None
        item.amount = 100
        item.order = 1
        item.save()

        item_values = item.get_nutritional_values()

        self.assertAlmostEqual(item_values.energy, ingredient.energy, 2)
        self.assertAlmostEqual(item_values.carbohydrates, ingredient.carbohydrates, 2)
        self.assertAlmostEqual(item_values.carbohydrates_sugar, None, 2)
        self.assertAlmostEqual(item_values.fat, ingredient.fat, 2)
        self.assertAlmostEqual(item_values.fat_saturated, ingredient.fat_saturated, 2)
        self.assertAlmostEqual(item_values.sodium, ingredient.sodium, 2)
        self.assertAlmostEqual(item_values.fiber, None, 2)

        meal_nutritional_values = meal.get_nutritional_values()
        self.assertEqual(item_values, meal_nutritional_values)

        plan_nutritional_values = plan.get_nutritional_values()
        self.assertEqual(meal_nutritional_values.energy, plan_nutritional_values['total'].energy)

        # One ingredient, 1 x unit 3
        item.delete()
        item = models.MealItem()
        item.meal = meal
        item.ingredient = ingredient
        item.order = 1
        item.amount = 1
        item.weight_unit_id = 3
        item.save()

        item_values = item.get_nutritional_values()

        self.assertAlmostEqual(item_values.energy, ingredient.energy * Decimal(12.0) / 100, 2)

        meal_nutritional_values = meal.get_nutritional_values()
        self.assertEqual(item_values, meal_nutritional_values)

        plan_nutritional_values = plan.get_nutritional_values()
        self.assertEqual(meal_nutritional_values, plan_nutritional_values['total'])

        # Add another ingredient, 200 gr
        item2 = models.MealItem()
        item2.meal = meal
        item2.ingredient = ingredient2
        item2.weight_unit_id = None
        item2.amount = 200
        item2.order = 1
        item2.save()

        item2_values = item2.get_nutritional_values()

        # result_total = {}
        self.assertAlmostEqual(item2_values.energy, 2 * ingredient2.energy)
        self.assertAlmostEqual(item2_values.carbohydrates, 2 * ingredient2.carbohydrates)
        self.assertAlmostEqual(item2_values.fat, 2 * ingredient2.fat)
        self.assertAlmostEqual(item2_values.protein, 2 * ingredient2.protein)

        meal_nutritional_values = meal.get_nutritional_values()

        plan_nutritional_values = plan.get_nutritional_values()
        self.assertEqual(meal_nutritional_values, plan_nutritional_values['total'])

        # Add another ingredient, 20 gr
        item3 = models.MealItem()
        item3.meal = meal
        item3.ingredient = ingredient3
        item3.weight_unit_id = None
        item3.amount = 20
        item3.order = 1
        item3.save()

        item3_values = item3.get_nutritional_values()
        self.assertAlmostEqual(item3_values.energy, ingredient3.energy * Decimal(20.0) / 100, 2)
        self.assertAlmostEqual(item3_values.protein, ingredient3.protein * Decimal(20.0) / 100, 2)
        self.assertAlmostEqual(
            item3_values.carbohydrates,
            ingredient3.carbohydrates * Decimal(20.0) / 100,
            2,
        )
        self.assertAlmostEqual(item3_values.fat, ingredient3.fat * Decimal(20.0) / 100, 2)

        meal_nutritional_values = meal.get_nutritional_values()

        plan_nutritional_values = plan.get_nutritional_values()
        self.assertEqual(meal_nutritional_values, plan_nutritional_values['total'])

    def test_calculations_user(self):
        """
        Tests the calculations
        :return:
        """
        self.user_login('test')
        plan = models.NutritionPlan.objects.get(pk=4)
        values = plan.get_nutritional_values()

        self.assertAlmostEqual(values['percent']['carbohydrates'], Decimal(29.79), 2)
        self.assertAlmostEqual(values['percent']['fat'], Decimal(20.36), 2)
        self.assertAlmostEqual(values['percent']['protein'], Decimal(26.06), 2)

        self.assertAlmostEqual(values['per_kg']['carbohydrates'], Decimal(4.96), 2)
        self.assertAlmostEqual(values['per_kg']['fat'], Decimal(1.51), 2)
        self.assertAlmostEqual(values['per_kg']['protein'], Decimal(4.33), 2)
