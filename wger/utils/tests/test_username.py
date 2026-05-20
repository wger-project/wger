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
from django.test import TestCase

# wger
from wger.utils.username import generate_username_suggestions


class TestGenerateUsernameSuggestions(TestCase):
    def test_returns_correct_count(self):
        """
        Should return the number of suggestions
        """
        result = generate_username_suggestions('john', count=3)
        self.assertEqual(len(result), 3)

    def test_suggestions_are_unique_in_db(self):
        """
        Suggestions should not exist in the database
        """
        suggestions = generate_username_suggestions('john', 100)
        taken = set(
            User.objects.filter(username__in=suggestions).values_list('username', flat=True)
        )
        for suggestion in suggestions:
            self.assertNotIn(suggestion, taken)

    def test_suggestions_start_with_base(self):
        """
        All suggestions should contain the base username
        """
        suggestions = generate_username_suggestions('john')
        for suggestion in suggestions:
            self.assertIn('john', suggestion)

    def test_strips_special_characters(self):
        """
        Special characters in the username should be stripped
        """
        suggestions = generate_username_suggestions('john.doe!!')
        for suggestion in suggestions:
            self.assertIn('johndoe', suggestion)

    def test_empty_username_falls_back_to_user(self):
        """
        If the username is all special characters, suggestions should fall back to 'user'
        """
        suggestions = generate_username_suggestions('!!!!!')
        for suggestion in suggestions:
            self.assertIn('user', suggestion)
