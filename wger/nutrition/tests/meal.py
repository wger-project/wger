# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

import datetime

from django.core.urlresolvers import reverse

from wger.nutrition.models import Meal
from wger.nutrition.models import NutritionPlan

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class EditMealTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a meal
    '''

    object_class = Meal
    url = 'meal-edit'
    pk = 5
    data = {'time': datetime.time(8, 12)}


class AddMealTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a Meal
    '''

    object_class = Meal
    url = reverse('meal-add', kwargs={'plan_pk': 4})
    pk = 12
    data = {'time': datetime.time(9, 2)}
    user_success = 'test'
    user_fail = 'admin'


class PlanOverviewTestCase(WorkoutManagerTestCase):
    '''
    Tests the nutrition plan overview
    '''

    def get_plan_overview(self, logged_in=False):
        '''
        Helper function to test the nutrition plan overview
        '''

        response = self.client.get(reverse('wger.nutrition.views.plan.overview'))

        # Page exists
        if logged_in:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['plans']), 3)
        else:
            self.assertEqual(response.status_code, 302)

    def test_dashboard_anonymous(self):
        '''
        Test the nutrition plan as anonymous user
        '''

        self.get_plan_overview()

    def test_dashboard_logged_in(self):
        '''
        Test the nutrition plan as a logged in user
        '''
        self.user_login()
        self.get_plan_overview(logged_in=True)


class PlanDetailTestCase(WorkoutManagerTestCase):
    '''
    Tests the nutrition plan detail view
    '''

    def get_plan_detail_page(self, fail=False):
        '''
        Helper function to test the plan detail view
        '''

        response = self.client.get(reverse('wger.nutrition.views.plan.view', kwargs={'id': 1}))

        # Page exists
        if fail:
            self.assertIn(response.status_code, (302, 404))
        else:
            self.assertEqual(response.status_code, 200)
            plan = NutritionPlan.objects.get(pk=1)
            self.assertEqual(response.context['plan'], plan)

    def test_dashboard_anonymous(self):
        '''
        Test the nutrition plan as anonymous user
        '''

        self.get_plan_detail_page(fail=True)

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
