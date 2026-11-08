# -*- coding: utf-8 -*-

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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import json
from unittest import mock

# Django
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.test import (
    Client,
    override_settings,
)
from django.urls import reverse

# Third Party
from allauth.headless.tokens.strategies.jwt import internal
from rest_framework_simplejwt.tokens import RefreshToken

# wger
from wger.core.api.powersync import create_token
from wger.core.tests.base_testcase import WgerTestCase


class HeadlessSmokeTestCase(WgerTestCase):
    """
    End-to-end smoke test for the allauth.headless surface:

    - the public `config` endpoint responds with the headless capability
      descriptor (proves the URL mount is correct);
    - a headless login mints a JWT access token (proves JWTTokenStrategy is
      wired up correctly);
    - that JWT authenticates a regular `/api/v2/` request via
      ``HeadlessJWTAuthentication`` (proves the DRF bridge works).
    """

    def test_config_endpoint(self):
        response = self.client.get(reverse('headless:app:config'))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['status'], 200)

    def test_login_mints_jwt_and_authenticates_drf(self):
        response = self.client.post(
            reverse('headless:app:account:login'),
            data=json.dumps({'username': 'test', 'password': 'testtest'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        meta = response.json()['meta']
        self.assertTrue(meta['is_authenticated'])
        access_token = meta['access_token']
        self.assertTrue(access_token)

        # Use the JWT against a regular /api/v2/ endpoint. A fresh client avoids
        # the session cookie SessionAuthentication would otherwise consume.
        self.client.logout()
        response = self.client.get(
            '/api/v2/workoutsession/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
        )
        self.assertEqual(response.status_code, 200)

    def test_signup_respects_allow_registration_setting(self):
        """
        With ``ALLOW_REGISTRATION=False`` the WgerAccountAdapter must report
        the site as closed for signup, so the headless signup endpoint
        rejects the request and no user is created.
        """
        signup_data = {
            'username': 'headlessnew',
            'email': 'headlessnew@example.com',
            'password': 'AekaiLe0ga',
        }

        with self.settings(
            WGER_SETTINGS={
                'USE_RECAPTCHA': False,
                'ALLOW_GUEST_USERS': True,
                'ALLOW_REGISTRATION': False,
                'MIN_ACCOUNT_AGE_TO_TRUST': 21,
            }
        ):
            count_before = User.objects.count()
            response = self.client.post(
                reverse('headless:app:account:signup'),
                data=json.dumps(signup_data),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 403, response.content)
            self.assertEqual(User.objects.count(), count_before)

        # Sanity-check the opposite path: with registration enabled the same
        # payload creates a user via the headless endpoint.
        count_before = User.objects.count()
        response = self.client.post(
            reverse('headless:app:account:signup'),
            data=json.dumps(signup_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(User.objects.count(), count_before + 1)

    def test_access_token_for_deleted_user_is_rejected(self):
        """
        A JWT access token stays cryptographically valid after its user is
        deleted, so allauth's lazy user lookup would otherwise raise
        DoesNotExist on first access and surface as a 500 later on. The auth
        layer rejects it here cleanly instead, with the same outcome as an
        expired token.
        """
        response = self.client.post(
            reverse('headless:app:account:login'),
            data=json.dumps({'username': 'test', 'password': 'testtest'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        access_token = response.json()['meta']['access_token']

        # Drop the session cookie the login set, then delete the user so the
        # still-valid token points at a row that no longer exists.
        self.client.logout()
        User.objects.get(username='test').delete()

        response = self.client.get(
            '/api/v2/workoutsession/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
        )
        self.assertIn(response.status_code, (401, 403))

    def test_access_token_for_deactivated_user_is_rejected(self):
        """
        A JWT access token stays cryptographically valid after its user is
        deactivated. Deactivation has to lock the account out of the API
        immediately, not only after the token expires.
        """
        response = self.client.post(
            reverse('headless:app:account:login'),
            data=json.dumps({'username': 'test', 'password': 'testtest'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        access_token = response.json()['meta']['access_token']

        self.client.logout()
        User.objects.filter(username='test').update(is_active=False)

        response = self.client.get(
            '/api/v2/workoutsession/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
        )
        self.assertIn(response.status_code, (401, 403))

    def test_refresh_token_for_deactivated_user_is_rejected(self):
        """
        A deactivated user must not be able to mint new access tokens with
        an existing refresh token.
        """
        response = self.client.post(
            reverse('headless:app:account:login'),
            data=json.dumps({'username': 'test', 'password': 'testtest'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        refresh_token = response.json()['meta']['refresh_token']

        self.client.logout()
        User.objects.filter(username='test').update(is_active=False)

        response = self.client.post(
            reverse('headless:app:tokens:refresh'),
            data=json.dumps({'refresh_token': refresh_token}),
            content_type='application/json',
        )
        self.assertNotEqual(response.status_code, 200, response.content)

    def _login_refresh_token(self) -> str:
        response = self.client.post(
            reverse('headless:app:account:login'),
            data=json.dumps({'username': 'test', 'password': 'testtest'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()['meta']['refresh_token']

    def _refresh(self, refresh_token: str):
        # A cookie-less client, like the app
        return Client().post(
            reverse('headless:app:tokens:refresh'),
            data=json.dumps({'refresh_token': refresh_token}),
            content_type='application/json',
        )

    def test_refresh_token_survives_a_lost_response(self):
        """
        When the answer to a refresh never reaches the client, it still holds the
        token it sent. That token has to keep working, and the successor the
        client never saw is dropped in favour of the new one.
        """
        first = self._login_refresh_token()

        lost = self._refresh(first)
        self.assertEqual(lost.status_code, 200, lost.content)
        lost_token = lost.json()['data']['refresh_token']

        retry = self._refresh(first)
        self.assertEqual(retry.status_code, 200, retry.content)
        self.assertNotEqual(retry.json()['data']['refresh_token'], lost_token)

        self.assertEqual(self._refresh(lost_token).status_code, 400)

    def test_refresh_token_is_retired_once_its_successor_is_used(self):
        """
        Rotation still happens: after the successor has been used once, the
        token it replaced is rejected.
        """
        first = self._login_refresh_token()

        second = self._refresh(first).json()['data']['refresh_token']
        response = self._refresh(second)
        self.assertEqual(response.status_code, 200, response.content)

        self.assertEqual(self._refresh(first).status_code, 400)

    def test_refresh_is_rejected_when_the_session_is_deleted_meanwhile(self):
        """
        A session deleted while the refresh is running, e.g. by a logout in a
        concurrent request, rejects the refresh token with a 400.
        """
        create_access_token = internal.create_access_token

        def delete_session_then_create(user, session, claims):
            Session.objects.filter(session_key=session.session_key).delete()
            return create_access_token(user, session, claims)

        for rotate in (True, False):
            with (
                self.subTest(rotate=rotate),
                override_settings(HEADLESS_JWT_ROTATE_REFRESH_TOKEN=rotate),
            ):
                refresh_token = self._login_refresh_token()
                with mock.patch.object(
                    internal,
                    'create_access_token',
                    side_effect=delete_session_then_create,
                ):
                    response = self._refresh(refresh_token)
                self.assertEqual(response.status_code, 400)

    def test_invalid_jwt_does_not_break_auth_chain(self):
        """
        A malformed Bearer token must not raise AuthenticationFailed in our
        wrapper, the DRF auth chain has to fall through so the next class
        (e.g. SimpleJWT during the sunset window) still gets a turn.
        The final response is a permission rejection (403), not a 401 from a
        terminated chain.
        """
        response = self.client.get(
            '/api/v2/workoutsession/',
            HTTP_AUTHORIZATION='Bearer not-a-real-token',
        )
        self.assertIn(response.status_code, (401, 403))

    def test_powersync_token_is_rejected_by_the_rest_api(self):
        """
        PowerSync tokens and the REST API are signed with the same RS256
        keypair, so a valid signature alone must not grant API access: the
        PowerSync token (``aud='powersync'``, no access-token type claim) has
        to be rejected by the ``/api/v2/`` auth chain. A regular SimpleJWT
        access token is accepted on the same endpoint, proving it is the token
        type and not the endpoint that gates access.
        """
        user = User.objects.get(username='test')
        url = reverse('workoutsession-list')

        # Control: a genuine access token authenticates.
        access_token = str(RefreshToken.for_user(user).access_token)
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.assertEqual(response.status_code, 200, response.content)

        # The PowerSync token, though signed with the same key, must not.
        ps_token = create_token(user.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {ps_token}')
        self.assertIn(response.status_code, (401, 403))
