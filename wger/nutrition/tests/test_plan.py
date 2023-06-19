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
from wger.core.tests.base_testcase import (
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
)
from wger.nutrition.models import NutritionPlan


class PlanRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        p = NutritionPlan.objects.get(pk=5)
        self.assertEqual("{0}".format(p), 'Description 1')

        p.description = ''
        p.save()
        self.assertEqual("{0}".format(p), 'Nutrition plan')


class PlanShareButtonTestCase(WgerTestCase):
    """
    Test that the share button is correctly displayed and hidden
    """

    def test_share_button(self):
        plan = NutritionPlan.objects.get(pk=5)
        url = plan.get_absolute_url()

        response = self.client.get(url)
        self.assertFalse(response.context['show_shariff'])

        self.user_login('admin')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('test')
        response = self.client.get(url)
        self.assertFalse(response.context['show_shariff'])


class PlanAccessTestCase(WgerTestCase):
    """
    Test accessing the workout page
    """

    def test_access_shared(self):
        """
        Test accessing the URL of a shared workout
        """
        plan = NutritionPlan.objects.get(pk=5)

        self.user_login('admin')
        response = self.client.get(plan.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        self.user_login('test')
        response = self.client.get(plan.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        self.user_logout()
        response = self.client.get(plan.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_access_not_shared(self):
        """
        Test accessing the URL of a private workout
        """
        plan = NutritionPlan.objects.get(pk=4)

        self.user_login('admin')
        response = self.client.get(plan.get_absolute_url())
        self.assertEqual(response.status_code, 403)

        self.user_login('test')
        response = self.client.get(plan.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        self.user_logout()
        response = self.client.get(plan.get_absolute_url())
        self.assertEqual(response.status_code, 403)


class DeletePlanTestCase(WgerDeleteTestCase):
    """
    Tests deleting a nutritional plan
    """

    object_class = NutritionPlan
    url = 'nutrition:plan:delete'
    pk = 2


class EditPlanTestCase(WgerEditTestCase):
    """
    Tests editing an ingredient
    """

    object_class = NutritionPlan
    url = 'nutrition:plan:edit'
    pk = 2
    data = {'description': 'My new description'}


class PlanDailyCaloriesTestCase(WgerTestCase):
    """
    Tests the handling of the daily calories in the plan page
    """

    def test_overview_no_calories(self):
        """
        Tests the overview page with no daily calories set
        """

        self.user_login('test')

        # Can't find goal calories text
        response = self.client.get(reverse('nutrition:plan:view', kwargs={'id': 1}))
        self.assertFalse(response.context['plan'].has_goal_calories)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'goal amount of calories')

    def test_overview_calories(self):
        """
        Tests the overview page with no daily calories set
        """

        # Plan has daily calories goal
        self.user_login('test')
        plan = NutritionPlan.objects.get(pk=1)
        plan.has_goal_calories = True
        plan.save()

        # Can find goal calories text
        response = self.client.get(reverse('nutrition:plan:view', kwargs={'id': 1}))
        self.assertTrue(response.context['plan'].has_goal_calories)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'goal amount of calories')

    def test_meal_overview(self):
        """
        Tests the meal overview row
        """

        # Plan has daily calories goal
        self.user_login('test')
        plan = NutritionPlan.objects.get(pk=1)
        plan.has_goal_calories = True
        plan.save()

        # Can find goal calories text
        response = self.client.get(reverse('nutrition:plan:view', kwargs={'id': 1}))
        meal = response.context['plan'].meal_set.select_related()[0]
        self.assertTrue(meal.get_nutritional_values()['energy'])


class PlanApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the nutritional plan overview resource
    """
    pk = 4
    resource = NutritionPlan
    private_resource = True
    special_endpoints = ('nutritional_values', )
    data = {'description': 'The description', 'language': 1}


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

        # test each Plan object's fields are equal
        for field in plan_fields:
            self.assertEqual(getattr(orig_plan, field), getattr(copied_plan, field))

        orig_plan_meals = orig_plan.meal_set.all()
        copied_plan_meals = copied_plan.meal_set.all()
        
        for meal_cnt, orig_meal in enumerate(orig_plan_meals):
            # test that the fields are equal for each Meal object for each Plan
            for field in meal_fields:
                self.assertEqual(getattr(orig_meal, field), getattr(copied_plan_meals[meal_cnt], field))

            orig_plan_meal_items = orig_plan_meals[meal_cnt].mealitem_set.all()
            copied_plan_meal_items = copied_plan_meals[meal_cnt].mealitem_set.all()

            # test that the fields are equal for each MealItem object for each Meal
            for item_cnt, orig_meal_item in enumerate(orig_plan_meal_items):
                for field in meal_item_fields:
                    self.assertEqual(getattr(orig_meal_item, field), getattr(copied_plan_meal_items[item_cnt], field))
