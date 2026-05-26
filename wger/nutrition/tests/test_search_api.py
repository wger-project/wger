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
from unittest.mock import patch

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.nutrition.models import Ingredient


class SearchIngredientApiTestCase(BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/ingredient/'

    def test_basic_search_logged_out(self):
        """
        Logged-out users are also allowed to use the search
        """
        response = self.client.get(self.url + '?name__search=test&language__code=en')
        result1 = response.data['results'][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(result1['name'], 'Ingredient, test, 2, organic, raw')
        self.assertEqual(result1['id'], 2)

    def test_basic_search_logged_in(self):
        """
        Logged-in users get the same results
        """
        self.authenticate('test')
        response = self.client.get(self.url + '?name__search=test&language__code=en')
        result1 = response.data['results'][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(result1['name'], 'Ingredient, test, 2, organic, raw')
        self.assertEqual(result1['id'], 2)

    def test_search_language_code_en_no_results(self):
        """
        The "Testzutat" ingredient should not be found when searching in English
        """
        response = self.client.get(self.url + '?name__search=Testzutat&language__code=en')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_search_language_code_de(self):
        """
        The "Testzutat" ingredient should be only found when searching in German
        """
        response = self.client.get(self.url + '?name__search=Testzutat&language__code=de')
        result1 = response.data['results'][0]

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result1['name'], 'Testzutat 123')
        self.assertEqual(result1['id'], 6)

    def test_search_several_language_codes(self):
        """
        Passing different language codes works correctly
        """
        response = self.client.get(self.url + '?name__search=guest&language__code=en,de')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_search_unknown_language_codes(self):
        """
        Unknown language codes are ignored
        """
        response = self.client.get(self.url + '?name__search=guest&language__code=en,de,kg')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_search_all_languages(self):
        """
        Disable all language filters
        """
        response = self.client.get(self.url + '?name__search=guest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 7)

    @patch('wger.nutrition.api.filtersets.IngredientFilterSet.search_barcode')
    def test_search_name_with_valid_barcode(self, mock_search_barcode):
        """
        Searching for an 8-14 digit number in the name field should trigger the OFF API lookup
        """
        mock_search_barcode.return_value = Ingredient.objects.none()
        self.client.get(self.url + '?name__search=1300000000000')

        args, kwargs = mock_search_barcode.call_args
        self.assertEqual(args[1], 'code')
        self.assertEqual(args[2], '1300000000000')

    @patch('wger.nutrition.api.filtersets.IngredientFilterSet.search_barcode')
    def test_search_name_with_text(self, mock_search_barcode):
        """
        Searching for a standard text string should fall back to full-text search
        """
        self.client.get(self.url + '?name__search=apples')
        mock_search_barcode.assert_not_called()

    @patch('wger.nutrition.api.filtersets.IngredientFilterSet.search_barcode')
    def test_search_name_with_short_number(self, mock_search_barcode):
        """
        Searching for a short number (<8) should fall back to full-text search
        """
        self.client.get(self.url + '?name__search=7000000')
        mock_search_barcode.assert_not_called()

    @patch('wger.nutrition.api.filtersets.IngredientFilterSet.search_barcode')
    def test_search_name_with_long_number(self, mock_search_barcode):
        """
        Searching for a long number (>14) should fall back to full-text search
        """
        self.client.get(self.url + '?name__search=150000000000000')
        mock_search_barcode.assert_not_called()

    @patch('wger.nutrition.api.filtersets.IngredientFilterSet.search_barcode')
    def test_search_name_returns_barcode(self, mock_search_barcode):
        """
        If search_barcode finds a match, it should return it
        """
        mock_search_barcode.return_value = Ingredient.objects.filter(pk=2)

        response = self.client.get(self.url + '?name__search=1300000000000')
        result1 = response.data['results'][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(result1['name'], 'Ingredient, test, 2, organic, raw')
        self.assertEqual(result1['id'], 2)

    def test_filter_nutriscore_exact(self):
        """
        Exact match on nutriscore returns only ingredients with that grade
        """
        response = self.client.get(self.url + '?nutriscore=a')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_filter_nutriscore_in(self):
        """
        `in` lookup accepts a comma-separated list of grades
        """
        response = self.client.get(self.url + '?nutriscore__in=a,b')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 7)

    def test_filter_nutriscore_lt(self):
        """
        `lt` lookup returns ingredients with a better grade (e.g. better than C → A, B)
        """
        response = self.client.get(self.url + '?nutriscore__lt=c')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 7)

    def test_filter_nutriscore_lte(self):
        """
        `lte` lookup is inclusive (e.g. C or better → A, B, C)
        """
        response = self.client.get(self.url + '?nutriscore__lte=c')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)

    def test_filter_nutriscore_gt(self):
        """
        `gt` lookup returns ingredients with a worse grade (e.g. worse than C → D, E)
        """
        response = self.client.get(self.url + '?nutriscore__gt=c')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_filter_nutriscore_gte(self):
        """
        `gte` lookup is inclusive (e.g. C or worse → C, D, E)
        """
        response = self.client.get(self.url + '?nutriscore__gte=c')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)

    def test_barcode_found_locally(self):
        """
        A barcode already in the database is returned without calling OFF
        """
        response = self.client.get(self.url + '?code=1234567890987654321')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], 1)

    @patch('wger.nutrition.api.filtersets.Ingredient.fetch_ingredient_from_off')
    def test_barcode_not_found_locally_off_succeeds(self, mock_fetch):
        """
        A barcode absent locally is fetched from OFF and the created ingredient is returned
        """
        mock_fetch.return_value = Ingredient.objects.get(pk=2)

        response = self.client.get(self.url + '?code=0000000000000')

        mock_fetch.assert_called_once_with('0000000000000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], 2)

    @patch('wger.nutrition.api.filtersets.Ingredient.fetch_ingredient_from_off')
    def test_barcode_not_found_locally_off_returns_none(self, mock_fetch):
        """
        A barcode unknown on OFF returns an empty result
        """
        mock_fetch.return_value = None

        response = self.client.get(self.url + '?code=0000000000000')

        mock_fetch.assert_called_once_with('0000000000000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
