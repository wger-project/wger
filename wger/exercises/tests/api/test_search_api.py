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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import json

# Django
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.base_testcase import WgerTestCase


class SearchExerciseApiTestCase(WgerTestCase):
    """
    Tests searching for exercises via the exerciseinfo endpoint's name__search filter
    """

    url = reverse('exerciseinfo-list')

    def search_exercise(self):
        """
        Helper function to test basic searching for exercises
        """

        # Search for "cool" should find exercise base containing "Very cool exercise"
        response = self.client.get(self.url, {'name__search': 'cool', 'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf8'))
        results = result['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['category']['name'], 'Another category')

        # Search for non-existent term should return no results
        response = self.client.get(self.url, {'name__search': 'Foobar', 'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result['results']), 0)

    def test_search_logged_out(self):
        """
        Logged-out users are also allowed to use the search
        """
        self.search_exercise()

    def test_search_logged_in(self):
        """
        Logged-in users get the same results
        """
        self.user_login('test')
        self.search_exercise()

    def test_search_language_code_en(self):
        """
        Explicitly passing the en language code
        """
        response = self.client.get(
            self.url,
            {'name__search': 'exercise', 'language__code': 'en', 'format': 'json'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf8'))
        self.assertGreaterEqual(len(result['results']), 1)

    def test_search_language_code_en_no_results(self):
        """
        The "Testübung" exercise should not be found when searching in English
        """
        response = self.client.get(
            self.url,
            {'name__search': 'Testübung', 'language__code': 'en', 'format': 'json'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result['results']), 0)

    def test_search_language_code_de(self):
        """
        The "Testübung" exercise should be found when searching in German
        """
        response = self.client.get(
            self.url,
            {'name__search': 'Testübung', 'language__code': 'de', 'format': 'json'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result['results']), 1)

    def test_search_several_language_codes(self):
        """
        Passing different language codes works correctly
        """
        response = self.client.get(
            self.url,
            {'name__search': 'demo', 'language__code': 'en,de', 'format': 'json'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf8'))
        self.assertGreaterEqual(len(result['results']), 1)
