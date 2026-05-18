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
        Submitting the preferences form persists the UserProfile settings as
        well as the first/last name on the related User.
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
            {**self.form_data, 'first_name': 'Test', 'last_name': 'User'},
        )

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('core:user:preferences'))
        user = User.objects.get(username='test')
        profile = user.userprofile
        self.assertTrue(profile.show_english_ingredients)
        self.assertTrue(profile.workout_reminder_active)
        self.assertEqual(profile.workout_reminder, 30)
        self.assertEqual(profile.workout_duration, 12)
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')

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

    def test_email_is_not_editable_from_preferences(self):
        """
        Email management was moved to allauth's EmailView: the preferences
        page no longer renders an email field and links to it instead.
        """
        self.user_login('test')
        response = self.client.get(reverse('core:user:preferences'))
        self.assertNotContains(response, 'name="email"')
        self.assertContains(response, reverse('account_email'))

    def test_account_email_page_renders(self):
        """The allauth email page uses wger's template and is reachable."""
        self.user_login('test')
        response = self.client.get(reverse('account_email'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/email_change.html')

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

    def test_invalid_field_shows_error_and_saves_nothing(self):
        """
        A validation error on the preferences form shows a banner and persists
        nothing — neither the UserProfile fields nor the first/last name.
        """
        self.user_login('test')

        user_before = User.objects.get(username='test')
        snapshot = {
            'first_name': user_before.first_name,
            'last_name': user_before.last_name,
            'height': user_before.userprofile.height,
            'birthdate': user_before.userprofile.birthdate,
        }

        response = self.client.post(
            reverse('core:user:preferences'),
            {
                **self.form_data,
                'first_name': 'Brand',
                'last_name': 'New',
                'birthdate': '01/01/2000',
                'height': '',  # required field left blank
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alert-danger')
        self.assertContains(response, 'Please correct the errors below.')

        user_after = User.objects.get(username='test')
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
