# -*- coding: utf-8 *-*

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
from django.contrib.auth.models import User

# Third Party
from rest_framework.authtoken.models import Token

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.api_token import create_token


class TokenHelperTestCase(WgerTestCase):
    """
    Tests the create_token helper
    """

    def test_make_token(self):
        """
        Test that create_token returns the user's existing token
        """
        user = User.objects.get(pk=2)
        self.assertEqual(Token.objects.filter(user=user).count(), 1)

        token_before = Token.objects.get(user=user).key
        token = create_token(user).key
        token_after = Token.objects.get(user=user).key

        self.assertEqual(token_before, token_after)
        self.assertEqual(token_before, token)

    def test_make_token_force_new(self):
        """
        Test that create_token returns the user's existing token
        """
        user = User.objects.get(pk=2)
        self.assertEqual(Token.objects.filter(user=user).count(), 1)

        token_before = Token.objects.get(user=user).key
        token = create_token(user, force_new=True).key
        token_after = Token.objects.get(user=user).key

        self.assertNotEqual(token_before, token_after)
        self.assertEqual(token, token_after)

    def test_make_token_new(self):
        """
        Test that create_token creates a token for users that don't have one
        """
        user = User.objects.get(pk=2)
        Token.objects.filter(user=user).delete()
        self.assertEqual(Token.objects.filter(user=user).count(), 0)

        create_token(user)
        self.assertEqual(Token.objects.filter(user=user).count(), 1)
