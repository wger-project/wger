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

import logging
import datetime
import decimal

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from wger.core.models import UserProfile
from wger.core.tests import api_base_test

from wger.utils.constants import TWOPLACES
from wger.weight.models import WeightEntry
from wger.manager.tests.testcase import WorkoutManagerTestCase

logger = logging.getLogger('wger.custom')


class PreferencesTestCase(WorkoutManagerTestCase):
    '''
    Tests the preferences page
    '''

    def test_preferences(self):
        '''
        Helper function to test the preferences page
        '''

        self.user_login('test')
        response = self.client.get(reverse('core:preferences'))

        profile = User.objects.get(username='test').userprofile
        self.assertFalse(profile.show_comments)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('preferences.html')

        # Change some preferences
        response = self.client.post(reverse('core:preferences'),
                                    {'show_comments': True,
                                     'show_english_ingredients': True,
                                     'email': 'my-new-email@example.com',
                                     'workout_reminder_active': True,
                                     'workout_reminder': '30',
                                     'workout_duration': 12,
                                     'notification_language': 2,
                                     'timer_active': False,
                                     'timer_pause': 100})

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('core:preferences'))
        profile = User.objects.get(username='test').userprofile
        self.assertTrue(profile.show_english_ingredients)
        self.assertTrue(profile.workout_reminder_active)
        self.assertEqual(profile.workout_reminder, 30)
        self.assertEqual(profile.workout_duration, 12)
        self.assertEqual(User.objects.get(username='test').email, 'my-new-email@example.com')

        # Change some preferences
        response = self.client.post(reverse('core:preferences'),
                                    {'show_comments': False,
                                     'show_english_ingredients': True,
                                     'email': '',
                                     'workout_reminder_active': True,
                                     'workout_reminder': 22,
                                     'workout_duration': 10,
                                     'notification_language': 2,
                                     'timer_active': True,
                                     'timer_pause': 40})

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('core:preferences'))
        profile = response.context['user'].userprofile
        self.assertFalse(profile.show_comments)
        self.assertTrue(profile.show_english_ingredients)
        self.assertEqual(response.context['user'].email, '')


class UserBodyweightTestCase(WorkoutManagerTestCase):
    '''
    Tests the body weight generation/update function
    '''

    def test_bodyweight_new(self):
        '''
        Tests that a new weight entry is created
        '''
        user = User.objects.get(pk=2)
        count_before = WeightEntry.objects.filter(user=user).count()

        entry = user.userprofile.user_bodyweight(80)
        count_after = WeightEntry.objects.filter(user=user).count()
        self.assertEqual(count_before, count_after - 1)
        self.assertEqual(entry.creation_date, datetime.date.today())

    def test_bodyweight_new_2(self):
        '''
        Tests that a new weight entry is created
        '''
        user = User.objects.get(pk=2)
        count_before = WeightEntry.objects.filter(user=user).count()
        last_entry = WeightEntry.objects.filter(user=user).latest()
        last_entry.creation_date = datetime.date.today() - datetime.timedelta(weeks=1)
        last_entry.save()

        entry = user.userprofile.user_bodyweight(80)
        count_after = WeightEntry.objects.filter(user=user).count()
        self.assertEqual(count_before, count_after - 1)
        self.assertEqual(entry.creation_date, datetime.date.today())

    def test_bodyweight_no_entries(self):
        '''
        Tests that a new weight entry is created if there are no weight entries
        '''
        user = User.objects.get(pk=2)
        WeightEntry.objects.filter(user=user).delete()

        count_before = WeightEntry.objects.filter(user=user).count()
        entry = user.userprofile.user_bodyweight(80)
        count_after = WeightEntry.objects.filter(user=user).count()
        self.assertEqual(count_before, count_after - 1)
        self.assertEqual(entry.creation_date, datetime.date.today())

    def test_bodyweight_edit(self):
        '''
        Tests that the last weight entry is edited
        '''
        user = User.objects.get(pk=2)
        last_entry = WeightEntry.objects.filter(user=user).latest()
        last_entry.creation_date = datetime.date.today() - datetime.timedelta(days=3)
        last_entry.save()

        count_before = WeightEntry.objects.filter(user=user).count()
        entry = user.userprofile.user_bodyweight(100)
        count_after = WeightEntry.objects.filter(user=user).count()
        self.assertEqual(count_before, count_after)
        self.assertEqual(entry.pk, last_entry.pk)
        self.assertEqual(entry.creation_date, last_entry.creation_date)
        self.assertEqual(entry.weight, 100)

    def test_bodyweight_edit_2(self):
        '''
        Tests that the last weight entry is edited
        '''
        user = User.objects.get(pk=2)
        last_entry = WeightEntry.objects.filter(user=user).latest()
        last_entry.creation_date = datetime.date.today()
        last_entry.save()

        count_before = WeightEntry.objects.filter(user=user).count()
        entry = user.userprofile.user_bodyweight(100)
        count_after = WeightEntry.objects.filter(user=user).count()
        self.assertEqual(count_before, count_after)
        self.assertEqual(entry.pk, last_entry.pk)
        self.assertEqual(entry.creation_date, last_entry.creation_date)
        self.assertEqual(entry.weight, 100)


class PreferencesCalculationsTestCase(WorkoutManagerTestCase):
    '''
    Tests the different calculation method in the user profile
    '''
    def test_last_weight_entry(self):
        '''
        Tests that the last weight entry is correctly returned
        '''
        self.user_login('test')
        user = User.objects.get(pk=2)
        entry = WeightEntry()
        entry.creation_date = datetime.datetime.today()
        entry.user = user
        entry.weight = 100
        entry.save()
        self.assertEqual(user.userprofile.weight, 100)
        entry.weight = 150
        entry.save()
        self.assertEqual(user.userprofile.weight, 150)

    def test_last_weight_entry_empty(self):
        '''
        Tests that the last weight entry is correctly returned if no matches
        '''
        self.user_login('test')
        user = User.objects.get(pk=2)
        WeightEntry.objects.filter(user=user).delete()
        self.assertEqual(user.userprofile.weight, 0)

    def test_bmi(self):
        '''
        Tests the BMI calculator
        '''

        self.user_login('test')

        user = User.objects.get(pk=2)
        bmi = user.userprofile.calculate_bmi()
        self.assertEqual(bmi, user.userprofile.weight / (1.80 * 1.80))

    def test_basal_metabolic_rate(self):
        '''
        Tests the BMR calculator
        '''

        self.user_login('test')

        # Male
        user = User.objects.get(pk=2)
        bmr = user.userprofile.calculate_basal_metabolic_rate()
        self.assertEqual(bmr, 1860)

        # Female
        user.userprofile.gender = "2"
        bmr = user.userprofile.calculate_basal_metabolic_rate()
        self.assertEqual(bmr, 1694)

        # Data missing
        user.userprofile.age = None
        bmr = user.userprofile.calculate_basal_metabolic_rate()
        self.assertEqual(bmr, 0)

    def test_calculate_activities(self):
        '''
        Tests the calories calculator for physical activities
        '''

        self.user_login('test')
        user = User.objects.get(pk=2)

        self.assertEqual(user.userprofile.calculate_activities(),
                         decimal.Decimal(1.57).quantize(TWOPLACES))

        # Gender has no influence
        user.userprofile.gender = "2"
        self.assertEqual(user.userprofile.calculate_activities(),
                         decimal.Decimal(1.57).quantize(TWOPLACES))

        # Change some of the parameters
        user.userprofile.work_intensity = '3'
        self.assertEqual(user.userprofile.calculate_activities(),
                         decimal.Decimal(1.80).quantize(TWOPLACES))

        user.userprofile.work_intensity = '2'
        user.userprofile.sport_intensity = '2'
        self.assertEqual(user.userprofile.calculate_activities(),
                         decimal.Decimal(1.52).quantize(TWOPLACES))


# TODO: the user can't delete or create new profiles
# class UserProfileApiTestCase(api_base_test.ApiBaseResourceTestCase):
#     '''
#     Tests the user preferences overview resource
#     '''
#     pk = 2
#     resource = UserProfile
#     private_resource = True
#     data = {'show_comments': False,
#             'show_english_ingredients': True,
#             'email': '',
#             'workout_reminder_active': True,
#             'workout_reminder': 22,
#             'workout_duration': 10,
#             'notification_language': 2,
#             'timer_active': True,
#             'timer_pause': 40}
