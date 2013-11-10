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

from wger.weight.models import WeightEntry
from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import ApiBaseResourceTestCase

logger = logging.getLogger('wger.custom')


class PreferencesTestCase(WorkoutManagerTestCase):
    '''
    Tests the preferences page
    '''

    def preferences(self):
        '''
        Helper function to test the preferences page
        '''

        # Fetch the preferences page
        response = self.client.get(reverse('preferences'))
        profile = response.context['user'].userprofile
        self.assertFalse(profile.show_comments)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('preferences.html')

        # Change some preferences
        response = self.client.post(reverse('preferences'),
                                    {'show_comments': 'on',
                                     'show_english_ingredients': 'on',
                                     'email': 'my-new-email@example.com'})

        #print response
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('preferences'))
        profile = response.context['user'].userprofile
        #self.assertTrue(profile.show_comments)
        self.assertTrue(profile.show_english_ingredients)
        self.assertEqual(response.context['user'].email, 'my-new-email@example.com')

        # Change some preferences
        response = self.client.post(reverse('preferences'),
                                    {'show_english_ingredients': 'on',
                                     'email': ''})

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('preferences'))
        profile = response.context['user'].userprofile
        self.assertFalse(profile.show_comments)
        self.assertTrue(profile.show_english_ingredients)
        self.assertEqual(response.context['user'].email, '')

    def test_preferences_logged_in(self):
        '''
        Tests the preferences page as a logged in user
        '''

        self.user_login('test')
        self.preferences()


class AjaxPreferencesTestCase(WorkoutManagerTestCase):
    '''
    Tests editing user preferences via AJAX
    '''

    def preferences(self):
        '''
        Helper function to test the preferences page
        '''

        # Set the 'show comments' option
        response = self.client.get(reverse('wger.manager.views.user.api_user_preferences'),
                                   {'do': 'set_show-comments',
                                    'show': '1'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual('Success', response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('preferences'))
        profile = response.context['user'].userprofile
        self.assertTrue(profile.show_comments)
        self.assertFalse(profile.show_english_ingredients)
        self.assertEqual(response.context['user'].email, 'test@example.com')

        # Set the 'english ingredients' option
        response = self.client.get(reverse('wger.manager.views.user.api_user_preferences'),
                                   {'do': 'set_english-ingredients',
                                    'show': '1'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual('Success', response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('preferences'))
        profile = response.context['user'].userprofile
        self.assertTrue(profile.show_comments)
        self.assertTrue(profile.show_english_ingredients)
        self.assertEqual(response.context['user'].email, 'test@example.com')

    def test_preferences_logged_in(self):
        '''
        Tests the preferences page as a logged in user
        '''

        self.user_login('test')
        self.preferences()


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

        self.assertEqual(user.userprofile.calculate_activities(), decimal.Decimal('1.57'))

        # Gender has no influence
        user.userprofile.gender = "2"
        self.assertEqual(user.userprofile.calculate_activities(), decimal.Decimal('1.57'))

        # Change some of the parameters
        user.userprofile.work_intensity = '3'
        self.assertEqual(user.userprofile.calculate_activities(), decimal.Decimal('1.80'))

        user.userprofile.work_intensity = '2'
        user.userprofile.sport_intensity = '2'
        self.assertEqual(user.userprofile.calculate_activities(), decimal.Decimal('1.52'))


class UserProfileApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests the user preferences overview resource
    '''
    resource = 'userprofile'
    resource_updatable = False


class UserProfileDetailApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests accessing a specific user preference (there's only one anyway)
    '''
    resource = 'userprofile/2'
