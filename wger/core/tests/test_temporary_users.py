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

# Standard Library
import datetime
import random

# Django
from django.contrib.auth.models import User
from django.core.management import call_command
from django.http import HttpRequest
from django.urls import reverse

# wger
from wger.core.demo import (
    create_demo_entries,
    create_temporary_user,
)
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import (
    Day,
    Schedule,
    ScheduleStep,
    Workout,
    WorkoutLog,
)
from wger.nutrition.models import (
    Meal,
    NutritionPlan,
)
from wger.weight.models import WeightEntry


class DemoUserTestCase(WgerTestCase):
    """
    Tests the demo user
    """

    @staticmethod
    def count_temp_users():
        """
        Counts the number of temporary users
        """
        return User.objects.filter(userprofile__is_temporary=1).count()

    def test_demo_data_no_guest_account(self):
        """
        Tests that the helper function creates demo data (workout, etc.)
        for the demo users
        """
        with self.settings(
            WGER_SETTINGS={
                'USE_RECAPTCHA': True,
                'ALLOW_REGISTRATION': True,
                'ALLOW_GUEST_USERS': False,
                'TWITTER': False,
                'MASTODON': False,
                'MIN_ACCOUNT_AGE_TO_TRUST': 21,
            }
        ):
            self.assertEqual(self.count_temp_users(), 1)
            self.client.get(reverse('core:dashboard'))
            self.assertEqual(self.count_temp_users(), 1)
            self.client.get(reverse('core:user:demo-entries'))
            self.assertEqual(self.count_temp_users(), 1)

    def test_demo_data_guest_account(self):
        """
        Tests that the helper function creates demo data (workout, etc.)
        for the demo users
        """
        self.client.get(reverse('core:dashboard'))
        self.assertEqual(self.count_temp_users(), 2)
        user = User.objects.get(pk=User.objects.latest('id').id)
        self.assertEqual(user.userprofile.is_temporary, True)
        self.assertEqual(Workout.objects.filter(user=user).count(), 0)

        self.client.get(reverse('core:user:demo-entries'))
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

    def test_demo_data_body_weight(self):
        """
        Tests that the helper function that creates demo data filters out
        existing dates for the weight entries
        """
        self.client.get(reverse('core:dashboard'))
        self.assertEqual(self.count_temp_users(), 2)
        user = User.objects.get(pk=4)

        temp = []
        for i in range(1, 5):
            creation_date = datetime.date.today() - datetime.timedelta(days=i)
            entry = WeightEntry(
                user=user,
                weight=80 + 0.5 * i + random.randint(1, 3),
                date=creation_date,
            )
            temp.append(entry)
        WeightEntry.objects.bulk_create(temp)
        create_demo_entries(user)

        # Body weight
        self.assertEqual(WeightEntry.objects.filter(user=user).count(), 19)

    def test_demo_user(self):
        """
        Tests that temporary users are automatically created when visiting
        URLs that need a user present
        """

        self.assertEqual(self.count_temp_users(), 1)

        # These pages should not create a user
        self.client.get(reverse('software:about-us'))
        self.assertEqual(self.count_temp_users(), 1)

        self.client.get(reverse('exercise:exercise:overview'))
        self.assertEqual(self.count_temp_users(), 1)

        self.client.get(reverse('nutrition:ingredient:list'))
        self.assertEqual(self.count_temp_users(), 1)

        self.user_logout()
        self.client.get(reverse('manager:workout:overview'))
        self.assertEqual(self.count_temp_users(), 1)

        self.user_logout()
        reverse('weight:overview')
        self.assertEqual(self.count_temp_users(), 1)

        self.user_logout()
        self.client.get(reverse('nutrition:plan:overview'))
        self.assertEqual(self.count_temp_users(), 1)

        # This page will create one
        self.client.get(reverse('core:dashboard'))
        self.assertEqual(self.count_temp_users(), 2)

        # The new user is automatically logged in, so no new user is created
        # after the first visit
        self.client.get(reverse('core:dashboard'))
        self.assertEqual(self.count_temp_users(), 2)

    def test_demo_user_notice(self):
        """
        Tests that demo users see a notice on every page
        """
        demo_notice_text = 'You are using a guest account'
        self.user_login('demo')
        self.assertContains(self.client.get(reverse('core:dashboard')), demo_notice_text)
        self.assertContains(self.client.get(reverse('manager:workout:overview')), demo_notice_text)
        self.assertContains(
            self.client.get(reverse('exercise:exercise:overview')), demo_notice_text
        )
        self.assertContains(self.client.get(reverse('nutrition:plan:overview')), demo_notice_text)
        self.assertContains(self.client.get(reverse('software:about-us')), demo_notice_text)

    def test_command_delete_old_users(self):
        """
        Tests that old demo users are deleted by the management command
        """

        request = HttpRequest()

        # Create some new demo users
        for i in range(0, 15):
            create_temporary_user(request)
        User.objects.filter().update(date_joined='2013-01-01 00:00+01:00')

        # These ones keep the date_joined field
        create_temporary_user(request)
        create_temporary_user(request)

        # Check and delete
        self.assertEqual(self.count_temp_users(), 18)
        call_command('delete-temp-users')
        self.assertEqual(self.count_temp_users(), 2)
