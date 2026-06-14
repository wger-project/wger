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

# Django
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.models import (
    Meal,
    MealItem,
    NutritionPlan,
)


class NutritionPlanInfoQueryCountTestCase(WgerTestCase):
    """
    The nutritionplaninfo endpoint must not issue a query per meal item.
    """

    def _build_plan(self, user, items_per_meal):
        plan = NutritionPlan.objects.create(user=user)
        for meal_order in range(2):
            meal = Meal.objects.create(plan=plan, order=meal_order + 1)
            for item_order in range(items_per_meal):
                MealItem.objects.create(
                    meal=meal,
                    ingredient_id=1,
                    amount=100,
                    order=item_order + 1,
                )
        return plan

    def _info_query_count(self, plan):
        url = reverse('nutritionplaninfo-detail', args=[plan.pk])
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return len(ctx.captured_queries)

    def test_query_count_independent_of_item_count(self):
        self.user_login('test')
        user = User.objects.get(username='test')

        # Same number of meals, different number of items per meal. With the
        # prefetch in place the query count must not grow with the items.
        count_few = self._info_query_count(self._build_plan(user, items_per_meal=1))
        count_many = self._info_query_count(self._build_plan(user, items_per_meal=5))

        self.assertEqual(count_few, count_many)
