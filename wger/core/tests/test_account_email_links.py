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
from django.core import mail
from django.test import override_settings
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase


@override_settings(SITE_URL='https://wger.example', ALLOWED_HOSTS=['*'])
class AccountEmailLinksTestCase(WgerTestCase):
    """
    Links with a secret key in account emails point to SITE_URL, not to the
    host of the request
    """

    forged_host = 'evil.example'

    def assert_link_on_site_url(self, link_path: str):
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body

        self.assertIn(f'https://wger.example{link_path}', body)
        self.assertNotIn(self.forged_host, body)

    def test_password_reset(self):
        """
        Password reset requested through the allauth form
        """
        response = self.client.post(
            reverse('account_reset_password'),
            {'email': 'test@example.com'},
            HTTP_HOST=self.forged_host,
        )

        self.assertEqual(response.status_code, 302)
        self.assert_link_on_site_url('/account/password/reset/key/')

    def test_password_reset_headless(self):
        """
        Password reset requested through the API used by the app
        """
        response = self.client.post(
            reverse('headless:app:account:request_password_reset'),
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json',
            HTTP_HOST=self.forged_host,
        )

        self.assertEqual(response.status_code, 200)
        self.assert_link_on_site_url('/account/password/reset/key/')

    def test_email_confirmation(self):
        """
        Confirmation email sent after signing up
        """
        response = self.client.post(
            reverse('account_signup'),
            {
                'username': 'newbie',
                'email': 'newbie@example.com',
                'password1': 'Sup3r-Secret-pw!',
                'password2': 'Sup3r-Secret-pw!',
            },
            HTTP_HOST=self.forged_host,
        )

        self.assertEqual(response.status_code, 302)
        self.assert_link_on_site_url('/account/confirm-email/')
