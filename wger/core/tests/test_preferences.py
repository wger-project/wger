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
import decimal
import logging

# Django
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.constants import TWOPLACES
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)


class PreferencesTestCase(WgerTestCase):
    """
    Tests the preferences page
    """

    def setUp(self):
        super().setUp()
        self.form_data = {
            'show_comments': True,
            'show_english_ingredients': True,
            'email': '',
            'first_name': '',
            'last_name': '',
            'workout_reminder_active': True,
            'workout_reminder': 30,
            'workout_duration': 12,
            'notification_language': 2,
            'num_days_weight_reminder': 10,
            'weight_unit': 'kg',
            'birthdate': '02/25/1987',
            'height': 180,
        }

    def test_preferences(self):
        """
        Helper function to test the preferences page
        """

        self.user_login('test')
        response = self.client.get(reverse('core:user:preferences'))

        profile = User.objects.get(username='test').userprofile
        self.assertFalse(profile.show_comments)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('preferences.html')

        # Change some preferences
        response = self.client.post(
            reverse('core:user:preferences'),
            {**self.form_data, 'email': 'my-new-email@example.com'},
        )

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('core:user:preferences'))
        profile = User.objects.get(username='test').userprofile
        self.assertTrue(profile.show_english_ingredients)
        self.assertTrue(profile.workout_reminder_active)
        self.assertEqual(profile.workout_reminder, 30)
        self.assertEqual(profile.workout_duration, 12)
        self.assertEqual(User.objects.get(username='test').email, 'my-new-email@example.com')

        # Change some preferences
        response = self.client.post(
            reverse('core:user:preferences'),
            {
                **self.form_data,
                'show_comments': False,
                'workout_reminder': 22,
                'workout_duration': 10,
                'weight_unit': 'lb',
                'height': 170,
            },
        )

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('core:user:preferences'))
        profile = response.context['user'].userprofile
        self.assertFalse(profile.show_comments)
        self.assertTrue(profile.show_english_ingredients)
        self.assertEqual(response.context['user'].email, '')

    def test_address(self):
        """
        Test that the address property works correctly
        """

        # Member2 has a contract
        user = User.objects.get(username='member2')
        self.assertEqual(
            user.userprofile.address,
            {
                'phone': '01234-567890',
                'zip_code': '00000',
                'street': 'Gassenstr. 14',
                'city': 'The City',
            },
        )

        # Test has no contracts
        user = User.objects.get(username='test')
        self.assertEqual(
            user.userprofile.address,
            {
                'phone': '',
                'zip_code': '',
                'street': '',
                'city': '',
            },
        )

    def test_duplicate_email_shows_error_and_saves_nothing(self):
        """
        Submitting the preferences form with an email that already belongs to
        another account must show an inline field error AND a top-of-page
        banner, and must not persist any of the submitted fields.

        Regression test for the silent-failure / half-save behavior in the
        preferences view: previously the duplicate-email error lived on a
        second form that wasn't put in the context, so the page reloaded
        silently while UserProfile fields had already been saved.
        """
        self.user_login('test')

        user_before = User.objects.get(username='test')
        snapshot = {
            'email': user_before.email,
            'first_name': user_before.first_name,
            'last_name': user_before.last_name,
            'height': user_before.userprofile.height,
            'birthdate': user_before.userprofile.birthdate,
        }

        response = self.client.post(
            reverse('core:user:preferences'),
            {
                **self.form_data,
                'email': 'admin@example.com',
                'first_name': 'Brand',
                'last_name': 'New',
                'birthdate': '01/01/2000',
                'height': 175,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This e-mail address is already in use.')
        self.assertContains(response, 'is-invalid')
        self.assertContains(response, 'invalid-feedback')
        self.assertContains(response, 'alert-danger')
        self.assertContains(response, 'Please correct the errors below.')

        user_after = User.objects.get(username='test')
        self.assertEqual(user_after.email, snapshot['email'])
        self.assertEqual(user_after.first_name, snapshot['first_name'])
        self.assertEqual(user_after.last_name, snapshot['last_name'])
        self.assertEqual(user_after.userprofile.height, snapshot['height'])
        self.assertEqual(user_after.userprofile.birthdate, snapshot['birthdate'])

    def test_invalid_email_format_shows_error_and_saves_nothing(self):
        """
        Submitting the preferences form with a malformed email must show an inline
        field error AND a banner, and not persist any submitted fields
        """
        self.user_login('test')

        user_before = User.objects.get(username='test')
        snapshot = {
            'email': user_before.email,
            'first_name': user_before.first_name,
            'last_name': user_before.last_name,
            'height': user_before.userprofile.height,
            'birthdate': user_before.userprofile.birthdate,
        }

        response = self.client.post(
            reverse('core:user:preferences'),
            {
                **self.form_data,
                'email': 'not an email',
                'first_name': 'Brand',
                'last_name': 'New',
                'birthdate': '01/01/2000',
                'height': 175,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address.')
        self.assertContains(response, 'is-invalid')
        self.assertContains(response, 'invalid-feedback')
        self.assertContains(response, 'alert-danger')
        self.assertContains(response, 'Please correct the errors below.')

        user_after = User.objects.get(username='test')
        self.assertEqual(user_after.email, snapshot['email'])
        self.assertEqual(user_after.first_name, snapshot['first_name'])
        self.assertEqual(user_after.last_name, snapshot['last_name'])
        self.assertEqual(user_after.userprofile.height, snapshot['height'])
        self.assertEqual(user_after.userprofile.birthdate, snapshot['birthdate'])


class UserBodyweightTestCase(WgerTestCase):
    """
    Tests the body weight generation/update function
    """

    def test_bodyweight_new(self):
        """
        Tests that a new weight entry is created
        """
        user = User.objects.get(pk=2)
        count_before = WeightEntry.objects.filter(user=user).count()

        entry = user.userprofile.user_bodyweight(80)
        count_after = WeightEntry.objects.filter(user=user).count()
        self.assertEqual(count_before, count_after - 1)
        self.assertEqual(entry.date.date(), timezone.now().date())

    def test_bodyweight_new_2(self):
        """
        Tests that a new weight entry is created
        """
        user = User.objects.get(pk=2)
        count_before = WeightEntry.objects.filter(user=user).count()
        last_entry = WeightEntry.objects.filter(user=user).latest()
        last_entry.date = timezone.now() - datetime.timedelta(weeks=1)
        last_entry.save()

        entry = user.userprofile.user_bodyweight(80)
        count_after = WeightEntry.objects.filter(user=user).count()
        self.assertEqual(count_before, count_after - 1)
        self.assertEqual(entry.date.date(), timezone.now().date())

    def test_bodyweight_new_3(self):
        """
        Tests that a new weight entry is created even if others exist today
        """
        user = User.objects.get(pk=2)
        count_before = WeightEntry.objects.filter(user=user).count()
        last_entry = WeightEntry.objects.filter(user=user).latest()
        last_entry.date = timezone.now() - datetime.timedelta(hours=1)
        last_entry.save()

        entry = user.userprofile.user_bodyweight(80)
        count_after = WeightEntry.objects.filter(user=user).count()
        self.assertEqual(count_before, count_after - 1)
        self.assertEqual(entry.date.date(), timezone.now().date())

    def test_bodyweight_no_entries(self):
        """
        Tests that a new weight entry is created if there are no weight entries
        """
        user = User.objects.get(pk=2)
        WeightEntry.objects.filter(user=user).delete()

        count_before = WeightEntry.objects.filter(user=user).count()
        entry = user.userprofile.user_bodyweight(80)
        count_after = WeightEntry.objects.filter(user=user).count()
        self.assertEqual(count_before, count_after - 1)
        self.assertEqual(entry.date.date(), timezone.now().date())


class PreferencesCalculationsTestCase(WgerTestCase):
    """
    Tests the different calculation method in the user profile
    """

    def test_last_weight_entry(self):
        """
        Tests that the last weight entry is correctly returned
        """
        self.user_login('test')
        user = User.objects.get(pk=2)
        entry = WeightEntry()
        entry.date = timezone.now()
        entry.user = user
        entry.weight = 100
        entry.save()
        self.assertEqual(user.userprofile.weight, 100)
        entry.weight = 150
        entry.save()
        self.assertEqual(user.userprofile.weight, 150)

    def test_last_weight_entry_empty(self):
        """
        Tests that the last weight entry is correctly returned if no matches
        """
        self.user_login('test')
        user = User.objects.get(pk=2)
        WeightEntry.objects.filter(user=user).delete()
        self.assertEqual(user.userprofile.weight, 0)

    def test_bmi(self):
        """
        Tests the BMI calculator
        """

        self.user_login('test')

        user = User.objects.get(pk=2)
        bmi = user.userprofile.calculate_bmi()
        self.assertEqual(
            bmi,
            user.userprofile.weight.quantize(TWOPLACES)
            / decimal.Decimal(1.80 * 1.80).quantize(TWOPLACES),
        )

    def test_basal_metabolic_rate(self):
        """
        Tests the BMR calculator
        """

        self.user_login('test')

        # Test User (pk=2)
        # 180 cm, 20 years
        # Last weight entry is 83 kg

        # Male
        user = User.objects.get(pk=2)
        bmr = user.userprofile.calculate_basal_metabolic_rate()
        self.assertEqual(bmr, 1860)

        # Female
        user.userprofile.gender = '2'
        bmr = user.userprofile.calculate_basal_metabolic_rate()
        self.assertEqual(bmr, 1694)

        # Data missing
        user.userprofile.age = None
        bmr = user.userprofile.calculate_basal_metabolic_rate()
        self.assertEqual(bmr, 0)

    def test_calculate_activities(self):
        """
        Tests the calories calculator for physical activities
        """

        self.user_login('test')
        user = User.objects.get(pk=2)

        self.assertEqual(
            user.userprofile.calculate_activities(), decimal.Decimal(1.57).quantize(TWOPLACES)
        )

        # Gender has no influence
        user.userprofile.gender = '2'
        self.assertEqual(
            user.userprofile.calculate_activities(), decimal.Decimal(1.57).quantize(TWOPLACES)
        )

        # Change some of the parameters
        user.userprofile.work_intensity = '3'
        self.assertEqual(
            user.userprofile.calculate_activities(), decimal.Decimal(1.80).quantize(TWOPLACES)
        )

        user.userprofile.work_intensity = '2'
        user.userprofile.sport_intensity = '2'
        self.assertEqual(
            user.userprofile.calculate_activities(), decimal.Decimal(1.52).quantize(TWOPLACES)
        )


# TODO: the user can't delete or create new profiles
# class UserProfileApiTestCase(api_base_test.ApiBaseResourceTestCase):
#     """
#     Tests the user preferences overview resource
#     """
#     pk = 2
#     resource = UserProfile
#     private_resource = True
#     data = {'show_comments': False,
#             'show_english_ingredients': True,
#             'email': '',
#             'workout_reminder_active': True,
#             'workout_reminder': 22,
#             'workout_duration': 10,
#             'notification_language': 2}
