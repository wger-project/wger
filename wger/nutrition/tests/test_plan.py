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
from django.urls import reverse, resolve

# wger
from wger.core.tests import api_base_test
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
        response = self.client.get(reverse("nutrition:plan:copy", kwargs={"pk": 2}))
        copied_plan_pk = int(resolve(response.url).kwargs["id"])
        copied_plan = NutritionPlan.objects.get(pk=copied_plan_pk)

        # fields for each object to test for equality
        plan_fields = ("user", "language", "description", "has_goal_calories",)
        meal_fields = ("name", "time", "order",)
        meal_item_fields = ("ingredient", "weight_unit", "order", "amount",)

        # test each Plan's fields are equal
        for field in plan_fields:
            self.assertEqual(getattr(orig_plan, field), getattr(copied_plan, field))

        orig_plan_meals = orig_plan.meal_set.all()
        copied_plan_meals = copied_plan.meal_set.all()

        for meal_cnt, orig_meal in enumerate(orig_plan_meals):
            # test that the fields are equal for each Meal for each Plan
            for field in meal_fields:
                self.assertEqual(getattr(orig_meal, field), getattr(copied_plan_meals[meal_cnt], field))

            orig_plan_meal_items = orig_plan_meals[meal_cnt].mealitem_set.all()
            copied_plan_meal_items = copied_plan_meals[meal_cnt].mealitem_set.all()

            # test that the fields are equal for each MealItem for each Meal
            for item_cnt, orig_meal_item in enumerate(orig_plan_meal_items):
                for field in meal_item_fields:
                    self.assertEqual(getattr(orig_meal_item, field), getattr(copied_plan_meal_items[item_cnt], field))
