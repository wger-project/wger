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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework.authtoken.models import Token

from wger.core.tests.base_testcase import WorkoutManagerTestCase

logger = logging.getLogger(__name__)


class ApiKeyTestCase(WorkoutManagerTestCase):
    '''
    Tests the API key page
    '''

    def test_api_key_page(self):
        '''
        Tests the API key generation page
        '''

        self.user_login('test')
        user = User.objects.get(username='test')

        # User already has a key
        response = self.client.get(reverse('core:user:api-key'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete current API key and generate new one')
        self.assertTrue(Token.objects.get(user=user))

        # User has no keys
        Token.objects.get(user=user).delete()
        response = self.client.get(reverse('core:user:api-key'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have no API key yet')
        self.assertRaises(Token.DoesNotExist, Token.objects.get, user=user)

    def test_api_key_page_generation(self):
        '''
        User generates a new key
        '''

        self.user_login('test')
        user = User.objects.get(username='test')
        key_before = Token.objects.get(user=user)

        response = self.client.get(reverse('core:user:api-key'), {'new_key': True})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response['Location'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete current API key and generate new one')

        key_after = Token.objects.get(user=user)
        self.assertTrue(key_after)

        # New key is different from the one before
        self.assertNotEqual(key_before.key, key_after.key)
