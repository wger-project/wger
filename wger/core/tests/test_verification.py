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
import re
from unittest import mock

# Django
from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils import translation

# Third Party
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from rest_framework.status import HTTP_200_OK

# wger
from wger.core.account_adapter import WgerAccountAdapter
from wger.core.tests.base_testcase import WgerTestCase


logger = logging.getLogger(__name__)


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


class AccountAdapterNotificationLanguageTestCase(WgerTestCase):
    """
    allauth emails are rendered in the recipient's notification language
    (UserProfile.notification_language), not the request's active language.
    """

    def _capture_send_language(self, email, context):
        """Record the active language at the moment super().send_mail runs."""
        captured = {}

        def fake_super(self, template_prefix, recipient, ctx):
            captured['language'] = translation.get_language()

        with mock.patch.object(DefaultAccountAdapter, 'send_mail', fake_super):
            with translation.override('en'):
                WgerAccountAdapter().send_mail('account/email/foo', email, context)

        return captured.get('language')

    def test_email_rendered_in_users_notification_language(self):
        user = User.objects.get(username='admin')
        # language pk=1 is German in the fixtures
        user.userprofile.notification_language_id = 1
        user.userprofile.save()

        language = self._capture_send_language(user.email, {'user': user})
        self.assertEqual(language, 'de')

    def test_falls_back_to_active_language_without_recipient(self):
        language = self._capture_send_language('nobody@example.com', {})
        self.assertEqual(language, 'en')


class UserProfileEmailReadOnlyTestCase(WgerTestCase):
    """
    Email is read-only on the userprofile endpoint; clients change addresses
    through the allauth.headless ``account/email`` endpoint instead.
    """

    URL = '/api/v2/userprofile/'

    def test_email_in_payload_is_ignored(self):
        self.user_login('test')
        original_email = User.objects.get(username='test').email

        response = self.client.post(
            self.URL,
            data=json.dumps({'email': 'attempted-change@example.com'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            User.objects.get(username='test').email,
            original_email,
        )
