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

# Django
from django.contrib.auth import get_user_model
from django.test import (
    Client,
    TestCase,
    override_settings,
)
from django.urls import reverse


User = get_user_model()

TRUSTED_IP = '192.0.2.1'
UNTRUSTED_IP = '198.51.100.5'

PROXY_HEADER_KEY = 'HTTP_X_REMOTE_USER'
USERNAME = 'admin'
NEW_USER_VALUE = 'auth_proxy_user'


class AuthProxyMiddlewareTests(TestCase):
    fixtures = (
        'test-languages',
        'gym_config',
    )

    def setUp(self):
        self.client = Client()
        self.existing_user = User.objects.create_user(
            username=USERNAME,
            password='password123',
        )
        self.protected_url = reverse('core:dashboard')

        self.login_url = reverse('core:user:login')[3:]
        """Login URL without the /en/ part"""

    # Helper to make requests with specific IP and header
    def make_request(self, ip_addr, header_value=None):
        headers = {}
        if header_value:
            headers[PROXY_HEADER_KEY] = header_value

        # Use REMOTE_ADDR to spoof the IP
        self.client.get(self.protected_url, REMOTE_ADDR=ip_addr, **headers)
        return self.client.get(self.protected_url)

    @override_settings(
        AUTH_PROXY_TRUSTED_IPS=[TRUSTED_IP],
        AUTH_PROXY_HEADER=PROXY_HEADER_KEY,
    )
    def test_success_trusted_ip_existing_user(self):
        response = self.make_request(TRUSTED_IP, USERNAME)
        self.assertEqual(response.status_code, 200)

        # Check if the correct user is logged into the session
        self.assertEqual(int(self.client.session['_auth_user_id']), self.existing_user.pk)

    @override_settings(
        AUTH_PROXY_TRUSTED_IPS=[TRUSTED_IP],
        AUTH_PROXY_HEADER=PROXY_HEADER_KEY,
        AUTH_PROXY_CREATE_UNKNOWN_USER=True,
    )
    def test_success_trusted_ip_new_user_created(self):
        self.assertFalse(User.objects.filter(username=NEW_USER_VALUE).exists())
        response = self.make_request(TRUSTED_IP, NEW_USER_VALUE)
        self.assertEqual(response.status_code, 200)

        # Verify user was created
        newly_created_user = User.objects.filter(username=NEW_USER_VALUE).first()
        self.assertIsNotNone(newly_created_user)
        self.assertEqual(int(self.client.session['_auth_user_id']), newly_created_user.pk)

    @override_settings(
        AUTH_PROXY_HEADER=PROXY_HEADER_KEY,
        AUTH_PROXY_TRUSTED_IPS=[TRUSTED_IP],
        WGER_SETTINGS={'ALLOW_GUEST_USERS': False}
    )
    def test_failure_untrusted_ip_header_present(self):
        """Should redirect to login because the middleware shouldn't authenticate"""

        response = self.make_request(UNTRUSTED_IP, USERNAME)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))
        self.assertNotIn('_auth_user_id', self.client.session)

    @override_settings(
        AUTH_PROXY_HEADER=PROXY_HEADER_KEY,
        AUTH_PROXY_TRUSTED_IPS=[TRUSTED_IP],
        WGER_SETTINGS={'ALLOW_GUEST_USERS': False}
    )
    def test_failure_trusted_ip_header_missing(self):
        """Should redirect to login"""
        response = self.make_request(TRUSTED_IP, header_value=None)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))
        self.assertNotIn('_auth_user_id', self.client.session)

    @override_settings(
        AUTH_PROXY_HEADER=PROXY_HEADER_KEY,
        AUTH_PROXY_TRUSTED_IPS=[TRUSTED_IP],
        AUTH_PROXY_CREATE_UNKNOWN_USER=False,
        WGER_SETTINGS={'ALLOW_GUEST_USERS': False}
    )
    def test_failure_trusted_ip_new_user_creation_disabled(self):
        self.assertFalse(User.objects.filter(username=NEW_USER_VALUE).exists())
        response = self.make_request(TRUSTED_IP, NEW_USER_VALUE)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

        # Verify user was NOT created
        self.assertFalse(User.objects.filter(username=NEW_USER_VALUE).exists())
        self.assertNotIn('_auth_user_id', self.client.session)

    @override_settings(
        AUTH_PROXY_TRUSTED_IPS=[TRUSTED_IP],
        AUTH_PROXY_HEADER='HTTP_X_DIFFERENT_USER',
        WGER_SETTINGS={'ALLOW_GUEST_USERS': False}
    )
    def test_alternate_header_name(self):
        # Request using the *correctly* configured header name
        self.client.get(
            self.protected_url,
            REMOTE_ADDR=TRUSTED_IP,
            HTTP_X_DIFFERENT_USER=USERNAME,
        )
        response_correct = self.client.get(self.protected_url)
        self.assertEqual(response_correct.status_code, 200)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.existing_user.pk)

        # Clear session before next request
        self.client.logout()

        # Request using the *default/wrong* header name should fail
        response_wrong1 = self.client.get(
            self.protected_url,
            REMOTE_ADDR=TRUSTED_IP,
            HTTP_X_REMOTE_USER=USERNAME,
        )
        response_wrong2 = self.client.get(self.protected_url)
        self.assertEqual(response_wrong1.status_code, 302)
        self.assertEqual(response_wrong2.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)
