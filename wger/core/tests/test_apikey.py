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
import logging

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# Third Party
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

# wger
from wger.core.tests.base_testcase import WgerTestCase


logger = logging.getLogger(__name__)


class ApiKeyTestCase(WgerTestCase):
    """
    Tests the API key page
    """

    def test_api_key_page(self):
        """
        Tests the API key generation page
        """

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
        """
        User generates a new key
        """

        self.user_login('test')
        user = User.objects.get(username='test')
        key_before = Token.objects.get(user=user)

        response = self.client.post(reverse('core:user:api-key'), {'new_key': True})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response['Location'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete current API key and generate new one')

        key_after = Token.objects.get(user=user)
        self.assertTrue(key_after)

        # New key is different from the one before
        self.assertNotEqual(key_before.key, key_after.key)

    def test_api_key_can_be_deleted_without_replacement(self):
        """
        The "Delete API key" button removes the token without immediately
        creating a new one. Distinct from rotation, which is the existing
        ``new_key`` flow.
        """
        self.user_login('test')
        user = User.objects.get(username='test')
        self.assertTrue(Token.objects.filter(user=user).exists())

        response = self.client.post(reverse('core:user:api-key'), {'delete_key': 'true'})
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Token.objects.filter(user=user).exists())

    def test_api_key_delete_requires_post(self):
        """
        Same CSRF-via-img-tag concern as rotation: a GET must not destroy
        the user's token.
        """
        self.user_login('test')
        user = User.objects.get(username='test')
        key_before = Token.objects.get(user=user).key

        response = self.client.get(reverse('core:user:api-key'), {'delete_key': 'true'})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.get(user=user).key, key_before)

    def test_api_key_rotation_requires_post(self):
        """
        Token rotation is a state-changing action and must not be triggered
        by a GET request — otherwise an attacker could embed a link or
        image that silently rotates a victim's token.
        """
        self.user_login('test')
        user = User.objects.get(username='test')
        key_before = Token.objects.get(user=user)

        response = self.client.get(reverse('core:user:api-key'), {'new_key': True})
        self.assertEqual(response.status_code, 200)

        key_after = Token.objects.get(user=user)
        self.assertEqual(key_before.key, key_after.key)

    def test_revoke_jwt_sessions_blacklists_outstanding_refresh_tokens(self):
        """
        The "Revoke all API sessions" button on /user/api-key has to
        blacklist every still-usable refresh token for the current user,
        and a previously-issued refresh must stop minting access tokens.
        """
        api = APIClient()
        obtain = api.post(
            '/api/v2/token',
            {'username': 'test', 'password': 'testtest'},
            format='json',
        )
        self.assertEqual(obtain.status_code, 200)
        old_refresh = obtain.data['refresh']

        # Sanity baseline before the revoke
        refresh_before = api.post(
            '/api/v2/token/refresh',
            {'refresh': old_refresh},
            format='json',
        )
        self.assertEqual(refresh_before.status_code, 200)

        self.user_login('test')
        response = self.client.post(
            reverse('core:user:api-key'),
            {'revoke_jwt_sessions': 'true'},
        )
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username='test')
        outstanding = OutstandingToken.objects.filter(user=user)
        self.assertTrue(outstanding.exists())
        for ot in outstanding:
            self.assertTrue(BlacklistedToken.objects.filter(token=ot).exists())

        refresh_after = api.post(
            '/api/v2/token/refresh',
            {'refresh': old_refresh},
            format='json',
        )
        self.assertEqual(refresh_after.status_code, 401)

    def test_revoke_jwt_sessions_only_touches_current_user(self):
        """
        Hitting the revoke button as user 'test' must not blacklist the
        refresh tokens of an unrelated user (e.g. 'admin'). Cross-user
        leakage here would be a one-call DoS.
        """
        api_admin = APIClient()
        admin_obtain = api_admin.post(
            '/api/v2/token',
            {'username': 'admin', 'password': 'adminadmin'},
            format='json',
        )
        self.assertEqual(admin_obtain.status_code, 200)
        admin_refresh = admin_obtain.data['refresh']

        self.user_login('test')
        response = self.client.post(
            reverse('core:user:api-key'),
            {'revoke_jwt_sessions': 'true'},
        )
        self.assertEqual(response.status_code, 302)

        # The admin's refresh token is untouched
        admin_refresh_after = api_admin.post(
            '/api/v2/token/refresh',
            {'refresh': admin_refresh},
            format='json',
        )
        self.assertEqual(admin_refresh_after.status_code, 200)

    def test_revoke_jwt_sessions_requires_post(self):
        """
        Same CSRF concern as ``new_key``: a GET must not blacklist anything,
        otherwise an attacker could embed an <img src=...> that silently
        kills the victim's mobile sessions.
        """
        api = APIClient()
        obtain = api.post(
            '/api/v2/token',
            {'username': 'test', 'password': 'testtest'},
            format='json',
        )
        old_refresh = obtain.data['refresh']

        self.user_login('test')
        response = self.client.get(
            reverse('core:user:api-key'),
            {'revoke_jwt_sessions': 'true'},
        )
        self.assertEqual(response.status_code, 200)

        refresh_after = api.post(
            '/api/v2/token/refresh',
            {'refresh': old_refresh},
            format='json',
        )
        self.assertEqual(refresh_after.status_code, 200)
