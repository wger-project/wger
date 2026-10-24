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

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# Third Party
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from allauth.mfa.totp.internal.auth import (
    TOTP,
    generate_totp_secret,
)

# wger
from wger.core.tests.base_testcase import WgerTestCase


# allauth's per-user limit for wrong second factor codes
FAILURE_LIMIT = 5

WRONG_CODE = '000000'


class MfaRateLimitTestCase(WgerTestCase):
    """
    Wrong second factor codes are throttled per user, on the web and the app
    """

    def setUp(self):
        super().setUp()
        user = User.objects.get(username='test')
        TOTP.activate(user, generate_totp_secret())
        self.recovery_code = RecoveryCodes.activate(user).get_unused_codes()[0]

    def web_login(self):
        response = self.client.post(
            reverse('core:user:login'),
            {'login': 'test', 'password': 'testtest'},
        )
        self.assertRedirects(response, reverse('mfa_authenticate'), fetch_redirect_response=False)

    def web_code(self, code: str):
        return self.client.post(reverse('mfa_authenticate'), {'code': code})

    def app_login(self) -> str:
        response = self.client.post(
            reverse('headless:app:account:login'),
            data=json.dumps({'username': 'test', 'password': 'testtest'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401, response.content)
        return response.json()['meta']['session_token']

    def app_code(self, session_token: str, code: str):
        return self.client.post(
            reverse('headless:app:mfa:authenticate'),
            data=json.dumps({'code': code}),
            content_type='application/json',
            HTTP_X_SESSION_TOKEN=session_token,
        )

    def test_web_valid_code_after_a_few_typos(self):
        self.web_login()
        self.web_code(WRONG_CODE)
        self.web_code(WRONG_CODE)

        response = self.web_code(self.recovery_code)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_web_valid_code_refused_after_the_limit(self):
        self.web_login()
        for _ in range(FAILURE_LIMIT):
            self.web_code(WRONG_CODE)

        response = self.web_code(self.recovery_code)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_app_valid_code_after_a_few_typos(self):
        token = self.app_login()
        self.app_code(token, WRONG_CODE)
        self.app_code(token, WRONG_CODE)

        response = self.app_code(token, self.recovery_code)
        self.assertEqual(response.status_code, 200, response.content)

    def test_app_valid_code_refused_after_the_limit(self):
        token = self.app_login()
        for _ in range(FAILURE_LIMIT):
            self.app_code(token, WRONG_CODE)

        response = self.app_code(token, self.recovery_code)
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(response.json()['errors'][0]['code'], 'too_many_login_attempts')

    def test_limit_survives_a_new_login(self):
        """Opening a fresh login with the password does not reset the budget"""
        token = self.app_login()
        for _ in range(FAILURE_LIMIT):
            self.app_code(token, WRONG_CODE)

        response = self.app_code(self.app_login(), self.recovery_code)
        self.assertEqual(response.status_code, 400, response.content)


class PasswordRateLimitTestCase(WgerTestCase):
    """
    Failed password logins are throttled per username, not per IP
    """

    def web_login(self, username: str, password: str):
        return self.client.post(
            reverse('core:user:login'),
            {'login': username, 'password': password},
        )

    def test_failures_for_one_user_do_not_block_others(self):
        """Behind the reverse proxy every client has the same IP"""
        for _ in range(10):
            self.web_login('admin', 'wrong password')

        response = self.web_login('test', 'testtest')
        self.assertTrue(response.wsgi_request.user.is_authenticated)
