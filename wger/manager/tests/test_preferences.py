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

from django.core.urlresolvers import reverse

from wger.manager.tests.testcase import WorkoutManagerTestCase

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
        profile = response.context['user'].get_profile()
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
        profile = response.context['user'].get_profile()
        #self.assertTrue(profile.show_comments)
        self.assertTrue(profile.show_english_ingredients)
        self.assertEqual(response.context['user'].email, 'my-new-email@example.com')

        # Change some preferences
        response = self.client.post(reverse('preferences'),
                                    {'show_english_ingredients': 'on',
                                     'email': ''})

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('preferences'))
        profile = response.context['user'].get_profile()
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
        profile = response.context['user'].get_profile()
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
        profile = response.context['user'].get_profile()
        self.assertTrue(profile.show_comments)
        self.assertTrue(profile.show_english_ingredients)
        self.assertEqual(response.context['user'].email, 'test@example.com')

    def test_preferences_logged_in(self):
        '''
        Tests the preferences page as a logged in user
        '''

        self.user_login('test')
        self.preferences()
