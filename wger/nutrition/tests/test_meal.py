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

import datetime

from django.core.urlresolvers import reverse
from wger.core.tests import api_base_test

from wger.nutrition.models import Meal
from wger.nutrition.models import NutritionPlan

from wger.manager.tests.testcase import (
    WorkoutManagerTestCase,
    WorkoutManagerEditTestCase,
    WorkoutManagerAddTestCase
)


class MealRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(Meal.objects.get(pk=1)), '1 Meal')


class EditMealTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a meal
    '''

    object_class = Meal
    url = 'nutrition:meal:edit'
    pk = 5
    data = {'time': datetime.time(8, 12)}


class AddMealTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a Meal
    '''

    object_class = Meal
    url = reverse('nutrition:meal:add', kwargs={'plan_pk': 4})
    data = {'time': datetime.time(9, 2)}
    user_success = 'test'
    user_fail = 'admin'


class PlanOverviewTestCase(WorkoutManagerTestCase):
    '''
    Tests the nutrition plan overview
    '''

    def get_plan_overview(self):
        '''
        Helper function to test the nutrition plan overview
        '''

        response = self.client.get(reverse('nutrition:plan:overview'))

        # Page exists
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['plans']), 3)

    def test_dashboard_logged_in(self):
        '''
        Test the nutrition plan as a logged in user
        '''
        self.user_login()
        self.get_plan_overview()


class PlanDetailTestCase(WorkoutManagerTestCase):
    '''
    Tests the nutrition plan detail view
    '''

    def get_plan_detail_page(self, fail=False):
        '''
        Helper function to test the plan detail view
        '''

        response = self.client.get(reverse('nutrition:plan:view', kwargs={'id': 1}))

        # Page exists
        if fail:
            self.assertIn(response.status_code, (302, 403, 404))
        else:
            self.assertEqual(response.status_code, 200)
            plan = NutritionPlan.objects.get(pk=1)
            self.assertEqual(response.context['plan'], plan)

    def test_dashboard_owner(self):
        '''
        Test the nutrition plan as the owner user
        '''
        self.user_login('test')
        self.get_plan_detail_page(fail=False)

    def test_dashboard_other(self):
        '''
        Test the nutrition plan as a differnt user
        '''
        self.user_login('admin')
        self.get_plan_detail_page(fail=True)


class MealApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the meal overview resource
    '''
    pk = 2
    resource = Meal
    private_resource = True
    special_endpoints = ('nutritional_values',)
    data = {'time': datetime.time(9, 2),
            'plan': 4,
            'order': 1}
