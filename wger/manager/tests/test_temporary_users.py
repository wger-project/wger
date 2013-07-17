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

from django.core.urlresolvers import reverse
from django.core.management import call_command

from django.contrib.auth.models import User

from wger.manager.models import ScheduleStep
from wger.manager.models import Schedule
from wger.manager.models import Workout
from wger.manager.models import Day
from wger.manager.models import WorkoutLog
from wger.nutrition.models import NutritionPlan
from wger.nutrition.models import Meal
from wger.weight.models import WeightEntry

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.demo import create_temporary_user
from wger.manager.demo import create_demo_entries


class DemoUserTestCase(WorkoutManagerTestCase):
    '''
    Tests the demo user
    '''

    def count_temp_users(self):
        '''
        Counts the number of temporary users
        '''
        return User.objects.filter(userprofile__is_temporary=1).count()

    def test_demo_data(self):
        '''
        Tests that the helper function creates demo data (workout, etc.)
        for the demo users
        '''
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(self.count_temp_users(), 2)
        user = User.objects.get(pk=4)
        self.assertEqual(user.get_profile().is_temporary, True)
        self.assertEqual(Workout.objects.filter(user=user).count(), 0)

        create_demo_entries(user)
        # Workout
        self.assertEqual(Workout.objects.filter(user=user).count(), 4)
        self.assertEqual(Day.objects.filter(training__user=user).count(), 2)
        self.assertEqual(WorkoutLog.objects.filter(user=user).count(), 56)

        # Schedule
        self.assertEqual(Schedule.objects.filter(user=user).count(), 3)
        self.assertEqual(ScheduleStep.objects.filter(schedule__user=user).count(), 6)

        # Nutrition
        self.assertEqual(NutritionPlan.objects.filter(user=user).count(), 1)
        self.assertEqual(Meal.objects.filter(plan__user=user).count(), 3)

        # Body weight
        self.assertEqual(WeightEntry.objects.filter(user=user).count(), 19)

    def test_demo_user(self):
        '''
        Tests that temporary users are automatically created when visiting
        URLs that need a user present
        '''

        self.assertEqual(self.count_temp_users(), 1)

        # These pages should not create a user
        response = self.client.get(reverse('contact'))
        self.assertEqual(self.count_temp_users(), 1)

        response = self.client.get(reverse('software:code'))
        self.assertEqual(self.count_temp_users(), 1)

        response = self.client.get(reverse('wger.exercises.views.exercises.overview'))
        self.assertEqual(self.count_temp_users(), 1)

        response = self.client.get(reverse('ingredient-list'))
        self.assertEqual(self.count_temp_users(), 1)

        # These pages will create one
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(self.count_temp_users(), 2)

        # The new user is automatically logged in, so no new user is created
        # after the first visit
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(self.count_temp_users(), 2)

        # Try some other pages
        self.user_logout()
        response = self.client.get(reverse('wger.manager.views.workout.overview'))
        self.assertEqual(self.count_temp_users(), 3)

        self.user_logout()
        response = self.client.get(reverse('weight-overview'))
        self.assertEqual(self.count_temp_users(), 4)

        self.user_logout()
        response = self.client.get(reverse('wger.nutrition.views.plan.overview'))
        self.assertEqual(self.count_temp_users(), 5)

    def test_demo_user_notice(self):
        '''
        Tests that demo users see a notice on every page
        '''
        demo_notice_text = 'You are using a guest account'
        self.user_login('demo')
        self.assertContains(self.client.get(reverse('dashboard')), demo_notice_text)
        self.assertContains(self.client.get(reverse('wger.manager.views.workout.overview')),
                            demo_notice_text)
        self.assertContains(self.client.get(reverse('wger.exercises.views.exercises.overview')),
                            demo_notice_text)
        self.assertContains(self.client.get(reverse('muscle-overview')), demo_notice_text)
        self.assertContains(self.client.get(reverse('wger.nutrition.views.plan.overview')),
                            demo_notice_text)
        self.assertContains(self.client.get(reverse('software:issues')), demo_notice_text)
        self.assertContains(self.client.get(reverse('software:license')), demo_notice_text)

    def test_command_delete_old_users(self):
        '''
        Tests that old demo users are deleted by the management command
        '''

        # Create some new demo users
        for i in range(0, 15):
            create_temporary_user()
        User.objects.filter().update(date_joined='2013-01-01 00:00+01:00')

        # These ones keep the date_joined field
        create_temporary_user()
        create_temporary_user()

        # Check and delete
        self.assertEqual(self.count_temp_users(), 18)
        call_command('delete-temp-users')
        self.assertEqual(self.count_temp_users(), 2)
