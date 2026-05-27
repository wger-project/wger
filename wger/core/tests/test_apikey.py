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
import json
import logging

# Django
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.urls import reverse

# Third Party
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.headless_long_lived import (
    LONG_LIVED_FLAG,
    list_long_lived_sessions,
    mint_long_lived_refresh_token,
)


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
        user = User.objects.get(username='test')
        old_refresh = str(RefreshToken.for_user(user))

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
        admin = User.objects.get(username='admin')
        admin_refresh = str(RefreshToken.for_user(admin))

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
        user = User.objects.get(username='test')
        old_refresh = str(RefreshToken.for_user(user))

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


class LongLivedRefreshTokenTestCase(WgerTestCase):
    """
    Mint, list, and revoke long-lived headless JWT refresh tokens from the
    /user/api-key page.
    """

    def test_generate_shows_token_once(self):
        """
        POST ``new_refresh_token`` mints a token and the next page render
        displays it exactly once. Refreshing the page does not show it again.
        """
        self.user_login('test')

        response = self.client.post(
            reverse('core:user:api-key'),
            {'new_refresh_token': 'true'},
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(response['Location'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Copy this token now.')
        self.assertContains(response, 'Revoke')

        # Refreshing must not show the token again.
        response = self.client.get(reverse('core:user:api-key'))
        self.assertNotContains(response, 'Copy this token now.')

    def test_generated_token_works_against_headless_refresh(self):
        """
        The minted refresh token actually validates against the headless
        token-refresh endpoint and returns a new access token.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        token = mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)

        api = APIClient()
        response = api.post(
            reverse('headless:app:tokens:refresh'),
            data=json.dumps({'refresh_token': token}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        self.assertIn('access_token', body['data'])

    def test_revoke_invalidates_token(self):
        """
        Revoking a long-lived session breaks the matching refresh token.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        token = mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)
        sessions = list_long_lived_sessions(user)
        self.assertEqual(len(sessions), 1)
        session_key = sessions[0].session_key

        response = self.client.post(
            reverse('core:user:api-key'),
            {'revoke_refresh_token': session_key},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list_long_lived_sessions(user), [])

        api = APIClient()
        refresh = api.post(
            reverse('headless:app:tokens:refresh'),
            data=json.dumps({'refresh_token': token}),
            content_type='application/json',
        )
        self.assertGreaterEqual(refresh.status_code, 400)

    def test_revoke_all(self):
        """
        Bulk revocation kills every long-lived session of the current user.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        for _ in range(3):
            mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)
        self.assertEqual(len(list_long_lived_sessions(user)), 3)

        response = self.client.post(
            reverse('core:user:api-key'),
            {'revoke_all_refresh_tokens': 'true'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list_long_lived_sessions(user), [])

    def test_revoke_cannot_target_other_users_session(self):
        """
        Posting another user's session_key must not delete that user's
        long-lived session — same cross-user defense as the JWT-revoke flow.
        """
        admin = User.objects.get(username='admin')
        mint_long_lived_refresh_token(admin, lifetime_seconds=120 * 86400)
        admin_sessions = list_long_lived_sessions(admin)
        self.assertEqual(len(admin_sessions), 1)
        admin_session_key = admin_sessions[0].session_key

        self.user_login('test')
        response = self.client.post(
            reverse('core:user:api-key'),
            {'revoke_refresh_token': admin_session_key},
        )
        self.assertEqual(response.status_code, 302)

        # Admin's long-lived session is still there.
        self.assertEqual(len(list_long_lived_sessions(admin)), 1)

    def test_generate_requires_post(self):
        """
        State-changing actions must not be triggered by a GET (CSRF defense).
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        response = self.client.get(
            reverse('core:user:api-key'),
            {'new_refresh_token': 'true'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list_long_lived_sessions(user), [])

    def test_browser_session_is_not_listed(self):
        """
        The user's regular browser session must not show up in the list of
        long-lived refresh tokens — only sessions tagged with
        ``LONG_LIVED_FLAG`` count.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        # The login above created a browser session; confirm it exists and is
        # *not* listed (no long-lived marker).
        self.assertEqual(list_long_lived_sessions(user), [])

        # And the marker really is what gates inclusion.
        browser_sessions = [
            s for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == str(user.pk)
        ]
        self.assertTrue(browser_sessions)
        for s in browser_sessions:
            self.assertFalse(s.get_decoded().get(LONG_LIVED_FLAG))
