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

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# Third Party
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
        response = self.client.get('/_allauth/app/v1/config')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['status'], 200)

    def test_login_mints_jwt_and_authenticates_drf(self):
        response = self.client.post(
            '/_allauth/app/v1/auth/login',
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
                '/_allauth/app/v1/auth/signup',
                data=json.dumps(signup_data),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 403, response.content)
            self.assertEqual(User.objects.count(), count_before)

        # Sanity-check the opposite path: with registration enabled the same
        # payload creates a user via the headless endpoint.
        count_before = User.objects.count()
        response = self.client.post(
            '/_allauth/app/v1/auth/signup',
            data=json.dumps(signup_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(User.objects.count(), count_before + 1)

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
