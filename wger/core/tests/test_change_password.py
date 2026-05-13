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
from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

# Third Party
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

# wger
from wger.core.tests.base_testcase import WgerTestCase


logger = logging.getLogger(__name__)


class ChangePasswordTestCase(WgerTestCase):
    """
    Tests changing the password of a registered user
    """

    def change_password(self, fail=True):
        # Fetch the change passwort page
        response = self.client.get(reverse('core:user:change-password'))

        if fail:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 200)

        # Fill in the change password form
        form_data = {
            'old_password': 'testtest',
            'new_password1': 'shuZoh2oGu7i',
            'new_password2': 'shuZoh2oGu7i',
        }

        response = self.client.post(reverse('core:user:change-password'), form_data)
        self.assertEqual(response.status_code, 302)

        # Check the new password was accepted
        user = User.objects.get(username='test')
        if fail:
            self.assertTrue(user.check_password('testtest'))
        else:
            self.assertTrue(user.check_password('shuZoh2oGu7i'))

    def test_change_password_anonymous(self):
        """
        Test changing a password as an anonymous user
        """

        self.change_password()

    def test_copy_workout_logged_in(self, fail=True):
        """
        Test changing a password as a logged in user
        """

        self.user_login('test')
        self.change_password(fail=False)

    def test_other_sessions_are_invalidated_after_password_change(self):
        """
        When the same user is signed in from two different browsers and
        changes their password in one of them, the other browser's
        session must no longer be authenticated.
        """
        protected_url = reverse('core:user:preferences')

        # Browser A logs in and confirms the protected page is reachable
        browser_a = Client()
        browser_a.login(username='test', password='testtest')
        self.assertEqual(browser_a.get(protected_url).status_code, 200)

        # Browser B logs in independently, also reaches the protected page
        browser_b = Client()
        browser_b.login(username='test', password='testtest')
        self.assertEqual(browser_b.get(protected_url).status_code, 200)

        # Browser A changes the password
        response = browser_a.post(
            reverse('core:user:change-password'),
            {
                'old_password': 'testtest',
                'new_password1': 'shuZoh2oGu7i',
                'new_password2': 'shuZoh2oGu7i',
            },
        )
        self.assertEqual(response.status_code, 302)

        # Browser A's session keeps working (update_session_auth_hash)
        self.assertEqual(browser_a.get(protected_url).status_code, 200)

        # Browser B's session is silently invalidated, the next request is treated
        # as anonymous and bounced to the login page. Note that ``@login_required``
        # redirects to ``settings.LOGIN_URL`` directly, without any locale prefix
        response = browser_b.get(protected_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(settings.LOGIN_URL))

    def test_password_change_does_not_revoke_api_credentials(self):
        """
        Password change is intentionally session-scoped. The DRF API key and
        any active JWT refresh tokens must keep working — they are managed
        explicitly via the ``/user/api-key`` page (rotate the key, revoke
        sessions). Same model as GitHub PATs. This test guards against the
        coupling being silently re-introduced.
        """
        user = User.objects.get(username='test')
        drf_token_key = Token.objects.get(user=user).key

        api = APIClient()
        obtain = api.post(
            '/api/v2/token',
            {'username': 'test', 'password': 'testtest'},
            format='json',
        )
        self.assertEqual(obtain.status_code, 200)
        old_refresh = obtain.data['refresh']

        self.user_login('test')
        response = self.client.post(
            reverse('core:user:change-password'),
            {
                'old_password': 'testtest',
                'new_password1': 'shuZoh2oGu7i',
                'new_password2': 'shuZoh2oGu7i',
            },
        )
        self.assertEqual(response.status_code, 302)

        # DRF token survives
        self.assertTrue(Token.objects.filter(user=user, key=drf_token_key).exists())
        api_drf = APIClient()
        api_drf.credentials(HTTP_AUTHORIZATION=f'Token {drf_token_key}')
        self.assertEqual(api_drf.get('/api/v2/weightentry/').status_code, 200)

        # JWT refresh survives
        refresh_after = api.post(
            '/api/v2/token/refresh',
            {'refresh': old_refresh},
            format='json',
        )
        self.assertEqual(refresh_after.status_code, 200)
