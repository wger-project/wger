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

# Django
from django.forms import model_to_dict
from django.urls import (
    resolve,
    reverse,
)

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.models import NutritionPlan


class PlanApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the nutritional plan overview resource

    TODO: setting overview_cached to true since get_nutritional_values is
          cached, but we don't really use it. This should be removed
    """

    pk = 4
    resource = NutritionPlan
    private_resource = True
    overview_cached = False
    special_endpoints = ('nutritional_values',)
    data = {'description': 'The description'}


class PlanCopyTestCase(WgerTestCase):
    def test_copy_plan(self):
        """
        Tests making a copy of a meal plan
        """
        self.user_login()
        orig_plan = NutritionPlan.objects.get(pk=2)
        response = self.client.get(reverse('nutrition:plan:copy', kwargs={'pk': 2}))
        copied_plan_pk = int(resolve(response.url).kwargs['id'])
        copied_plan = NutritionPlan.objects.get(pk=copied_plan_pk)

        # Convert plans to dictionaries and compare
        orig_plan_dict = model_to_dict(orig_plan, exclude=['id'])
        copied_plan_dict = model_to_dict(copied_plan, exclude=['id'])
        self.assertEqual(orig_plan_dict, copied_plan_dict)

        orig_plan_meals = orig_plan.meal_set.all()
        copied_plan_meals = copied_plan.meal_set.all()

        for orig_meal, copied_meal in zip(orig_plan_meals, copied_plan_meals):
            orig_meal_dict = model_to_dict(orig_meal, exclude=['id', 'plan'])
            copied_meal_dict = model_to_dict(copied_meal, exclude=['id', 'plan'])
            self.assertEqual(orig_meal_dict, copied_meal_dict)

            orig_meal_items = orig_meal.mealitem_set.all()
            copied_meal_items = copied_meal.mealitem_set.all()

            for orig_meal_item, copied_meal_item in zip(orig_meal_items, copied_meal_items):
                orig_meal_item_dict = model_to_dict(orig_meal_item, exclude=['id', 'meal'])
                copied_meal_item_dict = model_to_dict(copied_meal_item, exclude=['id', 'meal'])
                self.assertEqual(orig_meal_item_dict, copied_meal_item_dict)
