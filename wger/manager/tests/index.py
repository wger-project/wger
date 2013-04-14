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


from django.core.urlresolvers import reverse

from wger.nutrition.models import NutritionPlan
from wger.manager.models import Workout
from wger.weight.models import WeightEntry

from wger.manager.tests.testcase import WorkoutManagerTestCase


class DashboardTestCase(WorkoutManagerTestCase):
    '''
    Dashboard (landing page) test case
    '''

    def dashboard(self, logged_in=False):
        '''
        Helper function to test the dashboard
        '''

        response = self.client.get(reverse('index'))

        # Everybody is redirected
        self.assertEqual(response.status_code, 302)

        # Delete the objects so we can test adding them later
        NutritionPlan.objects.all().delete()
        Workout.objects.all().delete()
        WeightEntry.objects.all().delete()

        response = self.client.get(reverse('dashboard'))
        if logged_in:
            # There is something to send to the template
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['weight'])
            self.assertFalse(response.context['current_workout'])
            self.assertFalse(response.context['plan'])
            self.assertRaises(KeyError, lambda: response.context['weekdays'])

        else:
            # Anonymous users are still redirected to the login page
            self.assertEqual(response.status_code, 302)

        #
        # 1. Add a workout
        #
        self.client.get(reverse('wger.manager.views.workout.add'))
        response = self.client.get(reverse('dashboard'))

        if logged_in:
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['weight'])
            self.assertTrue(response.context['current_workout'])
            self.assertFalse(response.context['plan'])
            self.assertTrue(response.context['weekdays'])

        else:
            self.assertEqual(response.status_code, 302)

        #
        # 2. Add a nutrition plan
        #
        self.client.get(reverse('wger.nutrition.views.plan.add'))
        response = self.client.get(reverse('dashboard'))

        if logged_in:
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['weight'])
            self.assertTrue(response.context['current_workout'])
            self.assertTrue(response.context['plan'])
            self.assertTrue(response.context['weekdays'])

        else:
            self.assertEqual(response.status_code, 302)

        #
        # 3. Add a weight entry
        #
        self.client.post(reverse('weight-add'),
                         {'weight': 100,
                         'creation_date': '2012-01-01'},)
        response = self.client.get(reverse('dashboard'))

        if logged_in:
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['weight'])
            self.assertTrue(response.context['current_workout'])
            self.assertTrue(response.context['plan'])
            self.assertTrue(response.context['weekdays'])

        else:
            self.assertEqual(response.status_code, 302)

    def test_dashboard_anonymous(self):
        '''
        Test index page as anonymous user
        '''

        self.dashboard()

    def test_dashboard_logged_in(self):
        '''
        Test index page as a logged in user
        '''

        self.user_login('admin')
        self.dashboard(logged_in=True)
