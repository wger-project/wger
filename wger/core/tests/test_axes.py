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
from django.conf import settings
from django.test import override_settings
from django.urls import reverse

# Third Party
from axes.models import AccessAttempt
from axes.utils import reset

# wger
from wger.core.tests.base_testcase import WgerTestCase


FAILURE_LIMIT = 3


@override_settings(AXES_ENABLED=True, AXES_FAILURE_LIMIT=FAILURE_LIMIT)
class AxesLockoutTestCase(WgerTestCase):
    """
    Tests the brute force protection

    allauth's own login rate limit is switched off (see settings_global), so
    django-axes is the only thing standing between an attacker and unlimited
    password guessing.
    """

    def setUp(self):
        super().setUp()

        # The shared base class switches axes off for every test, undo that
        settings.AXES_ENABLED = True
        reset()

    def tearDown(self):
        reset()
        super().tearDown()

    def web_login(self, password: str):
        return self.client.post(
            reverse('core:user:login'),
            {'login': 'test', 'password': password},
        )

    def api_login(self, password: str):
        return self.client.post(
            reverse('headless:app:account:login'),
            data=json.dumps({'username': 'test', 'password': password}),
            content_type='application/json',
        )

    def assert_logged_in(self, response):
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_failed_attempts_are_recorded(self):
        self.web_login('wrong password')

        self.assertEqual(AccessAttempt.objects.count(), 1)

    def test_lockout_after_the_failure_limit(self):
        for _ in range(FAILURE_LIMIT):
            response = self.web_login('wrong password')
            self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Even the correct password is now refused
        response = self.web_login('testtest')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_works_below_the_limit(self):
        for _ in range(FAILURE_LIMIT - 1):
            self.web_login('wrong password')

        self.assert_logged_in(self.web_login('testtest'))

    def test_reset_unlocks_the_account(self):
        for _ in range(FAILURE_LIMIT):
            self.web_login('wrong password')

        reset()

        self.assert_logged_in(self.web_login('testtest'))

    def test_api_login_is_covered(self):
        """
        The API login endpoint has to be protected too, it is the reason
        allauth's own rate limiting was switched off
        """
        for _ in range(FAILURE_LIMIT):
            self.api_login('wrong password')

        response = self.api_login('testtest')
        self.assertNotEqual(response.status_code, 200, response.content)

    def test_api_and_web_share_the_same_counter(self):
        """
        Switching endpoints must not give an attacker a fresh budget
        """
        for _ in range(FAILURE_LIMIT):
            self.api_login('wrong password')

        response = self.web_login('testtest')
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class AxesDisabledInTestsTestCase(WgerTestCase):
    """
    The shared base test case switches axes off so the other tests can log in
    as many users as they need
    """

    def test_repeated_failures_do_not_lock_out(self):
        for _ in range(15):
            self.client.post(
                reverse('core:user:login'),
                {'login': 'test', 'password': 'wrong password'},
            )

        response = self.client.post(
            reverse('core:user:login'),
            {'login': 'test', 'password': 'testtest'},
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)
