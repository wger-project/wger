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
import re

# Django
from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from django.urls import reverse

# Third Party
from allauth.account.models import EmailAddress
from rest_framework.status import HTTP_200_OK

# wger
from wger.core.tests.base_testcase import WgerTestCase


logger = logging.getLogger(__name__)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailVerificationFromPreferencesTestCase(WgerTestCase):
    """
    Tests that clicking the verification link in the preferences sidebar
    sends a verification email via allauth.
    """

    def test_confirm_email_sends_mail_for_unverified_user(self):
        """
        An unverified user clicking confirm-email receives a verification email
        """

        # User 1 (admin) has verified=False in the fixtures
        self.user_login('admin')

        mail.outbox = []
        response = self.client.get(reverse('core:user:confirm-email'))

        # Redirects to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('core:dashboard'), response.url)

        # A verification email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('admin@example.com', mail.outbox[0].to)

    def test_confirm_email_link_verifies_email(self):
        """
        Following the confirmation link from the email marks the address as verified
        """

        # User 1 (admin) has verified=False in the fixtures
        self.user_login('admin')

        mail.outbox = []
        self.client.get(reverse('core:user:confirm-email'))
        self.assertEqual(len(mail.outbox), 1)

        # Extract the confirmation key from the email body
        email_body = mail.outbox[0].body
        match = re.search(r'/account/confirm-email/([^/\s]+)/', email_body)
        self.assertIsNotNone(match, 'Could not find confirmation link in email body')
        key = match.group(1)

        # Visit the confirmation URL (GET shows the page, POST confirms)
        confirm_url = reverse('account_confirm_email', args=[key])
        self.client.get(confirm_url)

        # The email should now be verified
        user = User.objects.get(username='admin')
        email_obj = EmailAddress.objects.get_for_user(user, user.email)
        self.assertTrue(email_obj.verified)

    def test_confirm_email_no_mail_for_verified_user(self):
        """
        A verified user clicking confirm-email does not receive a new email
        """

        # User 4 (trainer1) has verified=True in the fixtures
        self.user_login('trainer1')

        mail.outbox = []
        response = self.client.get(reverse('core:user:confirm-email'))

        # Redirects to dashboard
        self.assertEqual(response.status_code, 302)

        # No email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_confirm_email_requires_login(self):
        """
        Anonymous users are redirected to the login page
        """

        self.user_logout()
        response = self.client.get(reverse('core:user:confirm-email'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailVerificationFromAPITestCase(WgerTestCase):
    """
    Tests that requesting email verification via the API sends a
    verification email via allauth.
    """

    def test_verify_email_sends_mail_for_unverified_user(self):
        """
        POST to verify-email endpoint sends a verification email for unverified users
        """

        # User 1 (admin) has verified=False in the fixtures
        self.user_login('admin')

        mail.outbox = []
        response = self.client.get(
            reverse('userprofile-verify-email'),
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['status'], 'sent')

        # A verification email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('admin@example.com', mail.outbox[0].to)

    def test_verify_email_link_verifies_email(self):
        """
        Following the confirmation link from the API-triggered email marks the address as verified
        """

        # User 1 (admin) has verified=False in the fixtures
        self.user_login('admin')

        mail.outbox = []
        response = self.client.get(reverse('userprofile-verify-email'))
        self.assertEqual(response.data['status'], 'sent')
        self.assertEqual(len(mail.outbox), 1)

        # Extract the confirmation key from the email body
        email_body = mail.outbox[0].body
        match = re.search(r'/account/confirm-email/([^/\s]+)/', email_body)
        self.assertIsNotNone(match, 'Could not find confirmation link in email body')
        key = match.group(1)

        # Visit the confirmation URL (POST confirms)
        confirm_url = reverse('account_confirm_email', args=[key])
        self.client.get(confirm_url)

        # The email should now be verified
        user = User.objects.get(username='admin')
        email_obj = EmailAddress.objects.get_for_user(user, user.email)
        self.assertTrue(email_obj.verified)

    def test_verify_email_no_mail_for_verified_user(self):
        """
        POST to verify-email endpoint does not send email for already verified users
        """

        # User 4 (trainer1) has verified=True in the fixtures
        self.user_login('trainer1')

        mail.outbox = []
        response = self.client.get(
            reverse('userprofile-verify-email'),
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['status'], 'verified')

        # No email was sent
        self.assertEqual(len(mail.outbox), 0)
