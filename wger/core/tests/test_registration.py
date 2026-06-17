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
from io import StringIO

# Django
from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse

# Third Party
from allauth.account.models import EmailAddress

# wger
from wger.core.tests.base_testcase import WgerTestCase


logger = logging.getLogger(__name__)


class RegistrationTestCase(WgerTestCase):
    """
    Tests registering a new user via the registration form
    """

    def test_registration_captcha(self):
        """
        The signup form shows a reCAPTCHA field only when USE_RECAPTCHA is set.
        """
        with self.settings(
            WGER_SETTINGS={
                'USE_RECAPTCHA': True,
                'ALLOW_REGISTRATION': True,
                'ALLOW_GUEST_USERS': True,
                'MASTODON': False,
                'MIN_ACCOUNT_AGE_TO_TRUST': 21,
            }
        ):
            response = self.client.get(reverse('core:user:registration'))
            self.assertIn('captcha', response.context['form'].fields)

        with self.settings(
            WGER_SETTINGS={
                'USE_RECAPTCHA': False,
                'ALLOW_REGISTRATION': True,
                'ALLOW_GUEST_USERS': True,
                'MASTODON': False,
                'MIN_ACCOUNT_AGE_TO_TRUST': 21,
            }
        ):
            response = self.client.get(reverse('core:user:registration'))
            self.assertNotIn('captcha', response.context['form'].fields)

    def test_register(self):
        # Fetch the registration page
        response = self.client.get(reverse('core:user:registration'))
        self.assertEqual(response.status_code, 200)

        # Fill in the registration form
        registration_data = {
            'username': 'myusername',
            'password1': 'quai8fai7Zae',
            'password2': 'quai8fai7Zae',
            'email': 'not an email',
            'g-recaptcha-response': 'PASSED',
        }
        count_before = User.objects.count()

        # Wrong email
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

        # Correct email
        registration_data['email'] = 'my.email@example.com'
        response = self.client.post(reverse('core:user:registration'), registration_data)
        count_after = User.objects.count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(count_before + 1, count_after)
        self.user_logout()

        # Username already exists
        response = self.client.post(reverse('core:user:registration'), registration_data)
        count_after = User.objects.count()
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count_before + 1, count_after)

        # Email already exists
        registration_data['username'] = 'my.other.username'
        response = self.client.post(reverse('core:user:registration'), registration_data)
        count_after = User.objects.count()
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count_before + 1, count_after)

        # Password too short
        registration_data['password1'] = 'abc123'
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

        # Password is "password" (commonly used)
        registration_data['password1'] = 'password'
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

        # Password is entirely numeric
        registration_data['password1'] = '123456789'
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

        # Passwords don't match
        registration_data['password2'] = 'quai8fai7Zaeq'
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

        # First password is missing
        registration_data['password1'] = ''
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

        # Second password is missing
        registration_data['password2'] = ''
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

        # Username is too long
        long_user = (
            'my_username_is_'
            'wayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
            '_toooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo'
            '_loooooooooooooooooooooooooooooooooooooooooooooooooooooooooong'
        )
        registration_data['username'] = long_user
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

        # Username contains invalid symbol
        registration_data['username'] = 'username!'
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

        # Username is missing
        registration_data['username'] = ''
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

    def test_register_rejects_secondary_email_address(self):
        """
        Uniqueness must also cover allauth's ``EmailAddress`` table —
        secondary addresses owned by another user must not be claimable
        through the HTML registration form either.
        """
        admin = User.objects.get(username='admin')
        EmailAddress.objects.create(
            user=admin,
            email='secondary@example.com',
            primary=False,
            verified=False,
        )

        registration_data = {
            'username': 'newuser',
            'password1': 'quai8fai7Zae',
            'password2': 'quai8fai7Zae',
            'email': 'secondary@example.com',
            'g-recaptcha-response': 'PASSED',
        }
        count_before = User.objects.count()
        response = self.client.post(reverse('core:user:registration'), registration_data)

        # A passing form would 302-redirect after creating the user; the
        # rejection path re-renders the page with the form context.
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(User.objects.count(), count_before)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_registration_sends_verification_email(self):
        """
        Tests that a verification email is sent when a new user registers
        """

        registration_data = {
            'username': 'newuser',
            'password1': 'quai8fai7Zae',
            'password2': 'quai8fai7Zae',
            'email': 'newuser@example.com',
            'g-recaptcha-response': 'PASSED',
        }
        response = self.client.post(reverse('core:user:registration'), registration_data)
        self.assertEqual(response.status_code, 302)

        # A verification email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('newuser@example.com', mail.outbox[0].to)

        # An EmailAddress entry was created with verified=False
        user = User.objects.get(username='newuser')
        email_obj = EmailAddress.objects.get(user=user)
        self.assertEqual(email_obj.email, 'newuser@example.com')
        self.assertFalse(email_obj.verified)

    def test_registration_deactivated(self):
        """
        Test that with deactivated registration no users can register
        """

        with self.settings(
            WGER_SETTINGS={
                'USE_RECAPTCHA': False,
                'ALLOW_GUEST_USERS': True,
                'ALLOW_REGISTRATION': False,
                'MIN_ACCOUNT_AGE_TO_TRUST': 21,
            }
        ):
            # Fetch the registration page
            response = self.client.get(reverse('core:user:registration'))
            self.assertEqual(response.status_code, 302)

            # Fill in the registration form
            registration_data = {
                'username': 'myusername',
                'password1': 'Xee4fuev1ohj',
                'password2': 'Xee4fuev1ohj',
                'email': 'my.email@example.com',
                'g-recaptcha-response': 'PASSED',
            }
            count_before = User.objects.count()

            response = self.client.post(reverse('core:user:registration'), registration_data)
            count_after = User.objects.count()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_before, count_after)


class CreateUserCommand(WgerTestCase):
    def setUp(self):
        super(CreateUserCommand, self).setUp()
        self.out = StringIO()

    def test_access_api_user_creation(self):
        """Tests giving permission to register users via API"""

        user = User.objects.get(username='admin')
        self.assertFalse(user.userprofile.can_add_user)

        call_command('add-user-rest', 'admin', stdout=self.out, no_color=True)
        self.assertEqual('admin is now ALLOWED to add users via the API\n', self.out.getvalue())

        user = User.objects.get(username='admin')
        self.assertTrue(user.userprofile.can_add_user)

    def test_revoke_access_api_user_creation(self):
        """Tests revoking permission to register users via API"""

        user = User.objects.get(username='test')
        self.assertTrue(user.userprofile.can_add_user)

        call_command('add-user-rest', 'test', disable=True, stdout=self.out, no_color=True)
        self.assertEqual(
            'test is now DISABLED from adding users via the API\n',
            self.out.getvalue(),
        )

        user = User.objects.get(username='test')
        self.assertFalse(user.userprofile.can_add_user)

    def test_access_get_api_users(self):
        """Tests listing created users via API"""

        call_command('list-users-api', stdout=self.out, no_color=True)
        self.assertIn('Users created by test:', self.out.getvalue())
        self.assertIn('- trainer1', self.out.getvalue())
        self.assertIn('- trainer2', self.out.getvalue())
