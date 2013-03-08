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

import logging

from django.core.urlresolvers import reverse

from wger.manager.tests.testcase import WorkoutManagerTestCase

logger = logging.getLogger('workout_manager.custom')


class PreferencesTestCase(WorkoutManagerTestCase):
    '''
    Tests the preferences page
    '''

    def preferences(self, fail=True):
        '''
        Helper function to test the preferences page
        '''

        # Fetch the preferences page
        response = self.client.get(reverse('preferences'))

        if fail:
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed('index.html')
        else:
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed('preferences.html')

        # Change some preferences
        response = self.client.post(reverse('preferences'),
                                    {'show_comments': 'on',
                                    'show_english_ingredients': 'on',
                                    'email': 'my-new-email@example.com'})

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('preferences'))
        if not fail:
            profile = response.context['user'].get_profile()
            self.assertTrue(profile.show_comments)
            self.assertTrue(profile.show_english_ingredients)
            self.assertEqual(response.context['user'].email, 'my-new-email@example.com')

        # Change some preferences
        response = self.client.post(reverse('preferences'),
                                    {'show_english_ingredients': 'on',
                                    'email': ''})

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('preferences'))
        if not fail:
            profile = response.context['user'].get_profile()
            self.assertFalse(profile.show_comments)
            self.assertTrue(profile.show_english_ingredients)
            self.assertEqual(response.context['user'].email, '')

    def test_preferences_anonymous(self):
        '''
        Tests the preferences page as an anonymous user
        '''

        self.preferences(fail=True)

    def test_preferences_logged_in(self):
        '''
        Tests the preferences page as a logged in user
        '''

        self.user_login('test')
        self.preferences(fail=False)


class AjaxPreferencesTestCase(WorkoutManagerTestCase):
    '''
    Tests editing user preferences via AJAX
    '''

    def preferences(self, fail=True):
        '''
        Helper function to test the preferences page
        '''

        # Set the 'show comments' option
        response = self.client.get(reverse('wger.manager.views.user.api_user_preferences'),
                                   {'do': 'set_show-comments',
                                   'show': '1'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        if fail:
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed('index.html')
        else:
            self.assertEqual('Success', response.content)
            self.assertEqual(response.status_code, 200)

            response = self.client.get(reverse('preferences'))
            profile = response.context['user'].get_profile()
            self.assertTrue(profile.show_comments)
            self.assertFalse(profile.show_english_ingredients)
            self.assertEqual(response.context['user'].email, '')

        # Set the 'english ingredients' option
        response = self.client.get(reverse('wger.manager.views.user.api_user_preferences'),
                                   {'do': 'set_english-ingredients',
                                   'show': '1'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        if fail:
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed('index.html')
        else:
            self.assertEqual('Success', response.content)
            self.assertEqual(response.status_code, 200)

            response = self.client.get(reverse('preferences'))
            profile = response.context['user'].get_profile()
            self.assertTrue(profile.show_comments)
            self.assertTrue(profile.show_english_ingredients)
            self.assertEqual(response.context['user'].email, '')

    def test_preferences_anonymous(self):
        '''
        Tests the preferences page as an anonymous user
        '''

        self.preferences(fail=True)

    def test_preferences_logged_in(self):
        '''
        Tests the preferences page as a logged in user
        '''

        self.user_login('test')
        self.preferences(fail=False)
