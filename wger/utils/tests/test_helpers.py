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
import secrets
from unittest import mock

# Django
from django.contrib.auth.models import User
from django.test import SimpleTestCase

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.helpers import (
    EmailAuthBackend,
    password_generator,
)


class EmailAuthBackendTestCase(WgerTestCase):
    """
    Tests the email-based authentication backend
    """

    def setUp(self):
        super().setUp()
        self.backend = EmailAuthBackend()

    def test_authenticates_with_correct_email_and_password(self):
        user = User.objects.create_user('alice', 'alice@example.com', 'secret-pw')
        self.assertEqual(
            self.backend.authenticate(None, username='alice@example.com', password='secret-pw'),
            user,
        )

    def test_email_match_is_case_insensitive(self):
        """Login must work regardless of the casing of the stored email address."""
        user = User.objects.create_user('bob', 'Bob@Example.com', 'secret-pw')
        self.assertEqual(
            self.backend.authenticate(None, username='bob@example.com', password='secret-pw'),
            user,
        )

    def test_wrong_password_is_rejected(self):
        User.objects.create_user('carol', 'carol@example.com', 'secret-pw')
        self.assertIsNone(
            self.backend.authenticate(None, username='carol@example.com', password='wrong-pw')
        )

    def test_inactive_user_is_rejected(self):
        """A deactivated account must not be able to log in via its email address."""
        user = User.objects.create_user('dave', 'dave@example.com', 'secret-pw')
        user.is_active = False
        user.save()
        self.assertIsNone(
            self.backend.authenticate(None, username='dave@example.com', password='secret-pw')
        )

    def test_duplicate_email_does_not_raise(self):
        """email is not unique at the DB level — an ambiguous match must fail cleanly."""
        User.objects.create_user('eve1', 'shared@example.com', 'secret-pw')
        User.objects.create_user('eve2', 'shared@example.com', 'secret-pw')
        self.assertIsNone(
            self.backend.authenticate(None, username='shared@example.com', password='secret-pw')
        )

    def test_blank_username_does_not_match_emailless_users(self):
        """Guest users have an empty email — a blank login must not match them."""
        User.objects.create_user('frank', '', 'secret-pw')
        self.assertIsNone(self.backend.authenticate(None, username='', password='secret-pw'))
        self.assertIsNone(self.backend.authenticate(None, username=None, password='secret-pw'))


class PasswordGeneratorTestCase(SimpleTestCase):
    """
    Tests the password generator
    """

    def test_uses_cryptographically_secure_choice(self):
        """Generated passwords must come from the secrets CSPRNG, not the random module."""
        with mock.patch('secrets.choice', wraps=secrets.choice) as mock_choice:
            password_generator()
        mock_choice.assert_called()

    def test_respects_length_and_excludes_ambiguous_chars(self):
        password = password_generator(20)
        self.assertEqual(len(password), 20)
        self.assertFalse(set(password) & set('I1lO0o'))
