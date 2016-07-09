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

from django.core.urlresolvers import reverse

from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WorkoutManagerDeleteTestCase
from wger.core.tests.base_testcase import WorkoutManagerEditTestCase
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.nutrition.models import NutritionPlan


class PlanRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        p = NutritionPlan.objects.get(pk=5)
        self.assertEqual("{0}".format(p), 'Description 1')

        p.description = ''
        p.save()
        self.assertEqual("{0}".format(p), 'Nutrition plan')


class PlanShareButtonTestCase(WorkoutManagerTestCase):
    '''
    Test that the share button is correctly displayed and hidden
    '''

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


class PlanAccessTestCase(WorkoutManagerTestCase):
    '''
    Test accessing the workout page
    '''

    def test_access_shared(self):
        '''
        Test accessing the URL of a shared workout
        '''
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
        '''
        Test accessing the URL of a private workout
        '''
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


class DeletePlanTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a nutritional plan
    '''

    object_class = NutritionPlan
    url = 'nutrition:plan:delete'
    pk = 2


class EditPlanTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing an ingredient
    '''

    object_class = NutritionPlan
    url = 'nutrition:plan:edit'
    pk = 2
    data = {'description': 'My new description'}


class PlanDailyCaloriesTestCase(WorkoutManagerTestCase):
    '''
    Tests the handling of the daily calories in the plan page
    '''
    def test_overview_no_calories(self):
        '''
        Tests the overview page with no daily calories set
        '''

        self.user_login('test')

        # Can't find goal calories text
        response = self.client.get(reverse('nutrition:plan:view', kwargs={'id': 1}))
        self.assertFalse(response.context['plan'].has_goal_calories)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'goal amount of calories')

    def test_overview_calories(self):
        '''
        Tests the overview page with no daily calories set
        '''

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


class PlanApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the nutritional plan overview resource
    '''
    pk = 4
    resource = NutritionPlan
    private_resource = True
    special_endpoints = ('nutritional_values',)
    data = {'description': 'The description',
            'language': 1}
