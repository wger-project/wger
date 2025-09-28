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

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase


class SearchExerciseApiTestCase(BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/exercise/search/'

    def setUp(self):
        super().setUp()
        self.init_media_root()

    def test_basic_search_logged_out(self):
        """
        Logged-out users are also allowed to use the search
        """
        response = self.client.get(self.url + '?term=exercise')
        result1 = response.data['suggestions'][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['suggestions']), 4)
        self.assertEqual(result1['value'], 'An exercise')
        self.assertEqual(result1['data']['id'], 1)

    def test_basic_search_logged_in(self):
        """
        Logged-in users get the same results
        """
        self.authenticate('test')
        response = self.client.get(self.url + '?term=exercise')
        result1 = response.data['suggestions'][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['suggestions']), 4)
        self.assertEqual(result1['value'], 'An exercise')
        self.assertEqual(result1['data']['id'], 1)

    def test_search_language_code_en(self):
        """
        Explicitly passing the en language code (same as no code)
        """
        response = self.client.get(self.url + '?term=exercise&language=en')
        result1 = response.data['suggestions'][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['suggestions']), 4)
        self.assertEqual(result1['value'], 'An exercise')
        self.assertEqual(result1['data']['id'], 1)

    def test_search_language_code_en_no_results(self):
        """
        The "Testübung" exercise should not be found when searching in English
        """
        response = self.client.get(self.url + '?term=Testübung&language=en')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['suggestions']), 0)

    def test_search_language_code_de(self):
        """
        The "Testübung" exercise should be only found when searching in German
        """
        response = self.client.get(self.url + '?term=Testübung&language=de')
        result1 = response.data['suggestions'][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['suggestions']), 1)
        self.assertEqual(result1['value'], 'Weitere Testübung')
        self.assertEqual(result1['data']['id'], 7)

    def test_search_several_language_codes(self):
        """
        Passing different language codes works correctly
        """
        response = self.client.get(self.url + '?term=demo&language=en,de')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['suggestions']), 4)

    def test_search_all_languages(self):
        """
        Passing different language codes works correctly
        """
        response = self.client.get(self.url + '?term=demo&language=*')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['suggestions']), 4)
