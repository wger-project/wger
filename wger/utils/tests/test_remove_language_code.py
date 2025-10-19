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
from django.test import TestCase

# wger
from wger.utils.helpers import remove_language_code


class TestRemoveLanguageCode(TestCase):
    def test_remove_code(self):
        self.assertEqual(
            remove_language_code('/de/some/url/'),
            '/some/url/',
        )

    def test_no_language(self):
        self.assertEqual(
            remove_language_code('/api/v2/endpoint'),
            '/api/v2/endpoint',
        )
