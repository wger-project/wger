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
from django.contrib.auth.models import User
from django.urls import reverse

# wger
from wger.core.forms import (
    RegistrationForm,
    RegistrationFormNoCaptcha,
)
from wger.core.tests.base_testcase import WgerTestCase


logger = logging.getLogger(__name__)


class RegistrationTestCase(WgerTestCase):
    """
    Tests registering a new user
    """

    def test_registration_captcha(self):
        """
        Tests that the correct form is used depending on global
        configuration settings
        """
        with self.settings(
            WGER_SETTINGS={
                'USE_RECAPTCHA': True,
                'ALLOW_REGISTRATION': True,
                'ALLOW_GUEST_USERS': True,
                'TWITTER': False,
                'MASTODON': False,
                'MIN_ACCOUNT_AGE_TO_TRUST': 21,
            }
        ):
            response = self.client.get(reverse('core:user:registration'))
            self.assertIsInstance(response.context['form'], RegistrationForm)

        with self.settings(
            WGER_SETTINGS={
                'USE_RECAPTCHA': False,
                'ALLOW_REGISTRATION': True,
                'ALLOW_GUEST_USERS': True,
                'TWITTER': False,
                'MASTODON': False,
                'MIN_ACCOUNT_AGE_TO_TRUST': 21,
            }
        ):
            response = self.client.get(reverse('core:user:registration'))
            self.assertIsInstance(response.context['form'], RegistrationFormNoCaptcha)

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
