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

import logging
from decimal import Decimal

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.nutrition import models
from wger.utils.constants import TWOPLACES

logger = logging.getLogger(__name__)


class NutritionalValuesCalculationsTestCase(WorkoutManagerTestCase):
    '''
    Tests the nutritional values calculators in the different models
    '''

    def test_calculations(self):
        plan = models.NutritionPlan(user_id=1, language_id=1)
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

        result_item = item.get_nutritional_values()

        for i in result_item:
            self.assertEqual(result_item[i], Decimal(getattr(ingredient, i)).quantize(TWOPLACES))

        result_meal = meal.get_nutritional_values()
        self.assertEqual(result_item, result_meal)

        result_plan = plan.get_nutritional_values()
        self.assertEqual(result_meal, result_plan['total'])

        # One ingredient, 1 x unit 3
        item.delete()
        item = models.MealItem()
        item.meal = meal
        item.ingredient = ingredient
        item.order = 1
        item.amount = 1
        item.weight_unit_id = 3
        item.save()

        result_item = item.get_nutritional_values()

        for i in result_item:
            self.assertEqual(result_item[i],
                             (getattr(ingredient, i) * Decimal(12.0) / 100).quantize(TWOPLACES))

        result_meal = meal.get_nutritional_values()
        self.assertEqual(result_item, result_meal)

        result_plan = plan.get_nutritional_values()
        self.assertEqual(result_meal, result_plan['total'])

        # Add another ingredient, 200 gr
        item2 = models.MealItem()
        item2.meal = meal
        item2.ingredient = ingredient2
        item2.weight_unit_id = None
        item2.amount = 200
        item2.order = 1
        item2.save()

        result_item2 = item2.get_nutritional_values()

        result_total = {}
        for i in result_item2:
            self.assertEqual(result_item2[i], 2 * getattr(ingredient2, i))
            result_total[i] = result_item[i] + result_item2[i]

        result_meal = meal.get_nutritional_values()
        self.assertEqual(result_total, result_meal)

        result_plan = plan.get_nutritional_values()
        self.assertEqual(result_meal, result_plan['total'])

        # Add another ingredient, 20 gr
        item3 = models.MealItem()
        item3.meal = meal
        item3.ingredient = ingredient3
        item3.weight_unit_id = None
        item3.amount = 20
        item3.order = 1
        item3.save()

        result_item3 = item3.get_nutritional_values()

        for i in result_item3:
            self.assertEqual(result_item3[i],
                             (getattr(ingredient3, i) * Decimal(20.0) / 100).quantize(TWOPLACES))
            result_total[i] = result_total[i] + result_item3[i]

        result_meal = meal.get_nutritional_values()
        self.assertEqual(result_total, result_meal)

        result_plan = plan.get_nutritional_values()
        self.assertEqual(result_meal, result_plan['total'])

    def test_calculations_user(self):
        '''
        Tests the calculations
        :return:
        '''
        self.user_login('test')
        plan = models.NutritionPlan.objects.get(pk=4)
        values = plan.get_nutritional_values()

        self.assertEqual(values['percent']['carbohydrates'], Decimal(29.79).quantize(TWOPLACES))
        self.assertEqual(values['percent']['fat'], Decimal(20.36).quantize(TWOPLACES))
        self.assertEqual(values['percent']['protein'], Decimal(26.06).quantize(TWOPLACES))

        self.assertEqual(values['per_kg']['carbohydrates'], Decimal(4.96).quantize(TWOPLACES))
        self.assertEqual(values['per_kg']['fat'], Decimal(1.51).quantize(TWOPLACES))
        self.assertEqual(values['per_kg']['protein'], Decimal(4.33).quantize(TWOPLACES))
