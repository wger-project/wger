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
import datetime
import json
from decimal import Decimal
from unittest.mock import patch

# Django
from django.core.exceptions import ValidationError
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.models import Language
from wger.core.tests import api_base_test
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import (
    BaseTestCase,
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
)
from wger.nutrition.models import (
    Ingredient,
    Meal,
)
from wger.utils.constants import NUTRITION_TAB


class IngredientRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(str(Ingredient.objects.get(pk=1)), 'Test ingredient 1')


class DeleteIngredientTestCase(WgerDeleteTestCase):
    """
    Tests deleting an ingredient
    """

    object_class = Ingredient
    url = 'nutrition:ingredient:delete'
    pk = 1


class EditIngredientTestCase(WgerEditTestCase):
    """
    Tests editing an ingredient
    """

    object_class = Ingredient
    url = 'nutrition:ingredient:edit'
    pk = 1
    data = {
        'name': 'A new name',
        'sodium': 2,
        'energy': 200,
        'fat': 10,
        'carbohydrates_sugar': 5,
        'fat_saturated': 3.14,
        'fiber': 2.1,
        'protein': 20,
        'carbohydrates': 10,
        'license': 2,
        'license_author': 'me!',
    }

    def post_test_hook(self):
        """
        Test that the update date is correctly set
        """
        if self.current_user == 'admin':
            ingredient = Ingredient.objects.get(pk=1)
            self.assertEqual(
                ingredient.last_update.replace(microsecond=0),
                datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0),
            )


class AddIngredientTestCase(WgerAddTestCase):
    """
    Tests adding an ingredient
    """

    object_class = Ingredient
    url = 'nutrition:ingredient:add'
    user_fail = False
    data = {
        'name': 'A new ingredient',
        'sodium': 2,
        'energy': 200,
        'fat': 10,
        'carbohydrates_sugar': 5,
        'fat_saturated': 3.14,
        'fiber': 2.1,
        'protein': 20,
        'carbohydrates': 10,
        'license': 2,
        'license_author': 'me!',
    }

    def post_test_hook(self):
        """
        Test that the creation date and the status are correctly set
        """
        if self.current_user == 'admin':
            ingredient = Ingredient.objects.get(pk=self.pk_after)
            self.assertEqual(
                ingredient.created.replace(microsecond=0),
                datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0),
            )
        elif self.current_user == 'test':
            ingredient = Ingredient.objects.get(pk=self.pk_after)


class IngredientNameShortTestCase(WgerTestCase):
    """
    Tests that ingredient cannot have name with length less than 3
    """

    data = {
        'name': 'Ui',
        'sodium': 2,
        'energy': 200,
        'fat': 10,
        'carbohydrates_sugar': 5,
        'fat_saturated': 3.14,
        'fiber': 2.1,
        'protein': 20,
        'carbohydrates': 10,
        'license': 2,
        'license_author': 'me!',
    }

    def test_add_ingredient_short_name(self):
        """
        Test that ingredient cannot be added with name of length less than 3
        """
        self.user_login('admin')

        count_before = Ingredient.objects.count()

        response = self.client.post(reverse('nutrition:ingredient:add'), self.data)
        count_after = Ingredient.objects.count()
        self.assertEqual(response.status_code, 200)

        # Ingredient was not added
        self.assertEqual(count_before, count_after)

    def test_edit_ingredient_short_name(self):
        """
        Test that ingredient cannot be edited to name of length less than 3
        """
        self.user_login('admin')

        response = self.client.post(
            reverse('nutrition:ingredient:edit', kwargs={'pk': '1'}), self.data
        )
        self.assertEqual(response.status_code, 200)

        ingredient = Ingredient.objects.get(pk=1)
        # Ingredient was not edited
        self.assertNotEqual(ingredient.last_update.date(), datetime.date.today())


class IngredientDetailTestCase(WgerTestCase):
    """
    Tests the ingredient details page
    """

    def ingredient_detail(self, editor=False):
        """
        Tests the ingredient details page
        """

        response = self.client.get(reverse('nutrition:ingredient:view', kwargs={'pk': 6}))
        self.assertEqual(response.status_code, 200)

        # Correct tab is selected
        self.assertEqual(response.context['active_tab'], NUTRITION_TAB)
        self.assertTrue(response.context['ingredient'])

        # Only authorized users see the edit links
        if editor:
            self.assertContains(response, 'Edit')
            self.assertContains(response, 'Delete')
        else:
            self.assertNotContains(response, 'Edit')
            self.assertNotContains(response, 'Delete')

        # Non-existent ingredients throw a 404.
        response = self.client.get(reverse('nutrition:ingredient:view', kwargs={'pk': 42}))
        self.assertEqual(response.status_code, 404)

    def test_ingredient_detail_editor(self):
        """
        Tests the ingredient details page as a logged-in user with editor rights
        """

        self.user_login('admin')
        self.ingredient_detail(editor=True)

    def test_ingredient_detail_non_editor(self):
        """
        Tests the ingredient details page as a logged-in user without editor rights
        """

        self.user_login('test')
        self.ingredient_detail(editor=False)

    def test_ingredient_detail_logged_out(self):
        """
        Tests the ingredient details page as an anonymous (logged out) user
        """

        self.ingredient_detail(editor=False)


class IngredientSearchTestCase(WgerTestCase):
    """
    Tests the ingredient search functions
    """

    def search_ingredient(self, fail=True):
        """
        Helper function
        """

        response = self.client.get(reverse('ingredient-search'), {'term': 'test'})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result['suggestions']), 2)
        self.assertEqual(result['suggestions'][0]['value'], 'Ingredient, test, 2, organic, raw')
        self.assertEqual(result['suggestions'][0]['data']['id'], 2)
        suggestion_0_name = 'Ingredient, test, 2, organic, raw'
        self.assertEqual(result['suggestions'][0]['data']['name'], suggestion_0_name)
        self.assertEqual(result['suggestions'][0]['data']['image'], None)
        self.assertEqual(result['suggestions'][0]['data']['image_thumbnail'], None)
        self.assertEqual(result['suggestions'][1]['value'], 'Test ingredient 1')
        self.assertEqual(result['suggestions'][1]['data']['id'], 1)
        self.assertEqual(result['suggestions'][1]['data']['name'], 'Test ingredient 1')
        self.assertEqual(result['suggestions'][1]['data']['image'], None)
        self.assertEqual(result['suggestions'][1]['data']['image_thumbnail'], None)

    def test_search_ingredient_anonymous(self):
        """
        Test searching for an ingredient by an anonymous user
        """

        self.search_ingredient()

    def test_search_ingredient_logged_in(self):
        """
        Test searching for an ingredient by a logged-in user
        """

        self.user_login('test')
        self.search_ingredient()


class IngredientValuesTestCase(WgerTestCase):
    """
    Tests the nutritional value calculator for an ingredient
    """

    def calculate_value(self):
        """
        Helper function
        """

        # Get the nutritional values in 1 gram of product
        response = self.client.get(
            reverse('api-ingredient-get-values', kwargs={'pk': 1}),
            {'amount': 1, 'ingredient': 1, 'unit': ''},
        )

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result), 8)
        self.assertEqual(
            result,
            {
                'sodium': 0.00549,
                'energy': 1.76,
                # 'energy_kilojoule': '7.36',
                'fat': 0.0819,
                'carbohydrates_sugar': None,
                'fat_saturated': 0.03244,
                'fiber': None,
                'protein': 0.2563,
                'carbohydrates': 0.00125,
            },
        )

        # Get the nutritional values in 1 unit of product
        response = self.client.get(
            reverse('api-ingredient-get-values', kwargs={'pk': 1}),
            {'amount': 1, 'ingredient': 1, 'unit': 2},
        )

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result), 8)
        self.assertEqual(
            result,
            {
                'sodium': 0.612135,
                'energy': 196.24,
                # 'energy_kilojoule': '821.07',
                'fat': 9.13185,
                'carbohydrates_sugar': None,
                'fat_saturated': 3.61706,
                'fiber': None,
                'protein': 28.57745,
                'carbohydrates': 0.139375,
            },
        )

    def test_calculate_value_anonymous(self):
        """
        Calculate the nutritional values as an anonymous user
        """

        self.calculate_value()

    def test_calculate_value_logged_in(self):
        """
        Calculate the nutritional values as a logged-in user
        """

        self.user_login('test')
        self.calculate_value()


class IngredientTestCase(WgerTestCase):
    """
    Tests other ingredient functions
    """

    def test_compare(self):
        """
        Tests the custom compare method based on values
        """
        language = Language.objects.get(pk=1)

        ingredient1 = Ingredient.objects.get(pk=1)
        ingredient2 = Ingredient.objects.get(pk=1)
        ingredient2.name = 'A different name altogether'
        self.assertFalse(ingredient1 == ingredient2)

        ingredient1 = Ingredient()
        ingredient1.name = 'ingredient name'
        ingredient1.energy = 150
        ingredient1.protein = 30
        ingredient1.language = language

        ingredient2 = Ingredient()
        ingredient2.name = 'ingredient name'
        ingredient2.energy = 150
        ingredient2.language = language
        self.assertFalse(ingredient1 == ingredient2)

        ingredient2.protein = 31
        self.assertFalse(ingredient1 == ingredient2)

        ingredient2.protein = None
        self.assertFalse(ingredient1 == ingredient2)

        ingredient2.protein = 30
        self.assertEqual(ingredient1, ingredient2)

        meal = Meal.objects.get(pk=1)
        self.assertFalse(ingredient1 == meal)

    def test_total_energy(self):
        """
        Tests the custom clean() method
        """
        self.user_login('admin')

        # Values OK
        ingredient = Ingredient()
        ingredient.name = 'FooBar, cooked, with salt'
        ingredient.energy = 50
        ingredient.protein = 0.5
        ingredient.carbohydrates = 12
        ingredient.fat = Decimal('0.1')
        ingredient.language_id = 1
        self.assertFalse(ingredient.full_clean())

        # Values wrong
        ingredient.protein = 20
        self.assertRaises(ValidationError, ingredient.full_clean)

        ingredient.protein = 0.5
        ingredient.fat = 5
        self.assertRaises(ValidationError, ingredient.full_clean)

        ingredient.fat = 0.1
        ingredient.carbohydrates = 20
        self.assertRaises(ValidationError, ingredient.full_clean)

        ingredient.fat = 5
        ingredient.carbohydrates = 20
        self.assertRaises(ValidationError, ingredient.full_clean)


class IngredientApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the ingredient API resource
    """

    pk = 4
    resource = Ingredient
    private_resource = False
    overview_cached = True
    data = {'language': 1, 'license': 2}


class IngredientModelTestCase(WgerTestCase):
    """
    Tests the ingredient model functions
    """

    def setUp(self):
        super().setUp()
        self.off_response = {
            'code': '1234',
            'lang': 'de',
            'product_name': 'Foo with chocolate',
            'generic_name': 'Foo with chocolate, 250g package',
            'brands': 'The bar company',
            'editors_tags': ['open food facts', 'MrX'],
            'nutriments': {
                'energy-kcal_100g': 120,
                'proteins_100g': 10,
                'carbohydrates_100g': 20,
                'sugars_100g': 30,
                'fat_100g': 40,
                'saturated-fat_100g': 11,
                'sodium_100g': 5,
                'fiber_100g': None,
            },
        }

        self.off_response_no_results = None

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_success(self, mock_api):
        """
        Tests creating an ingredient from OFF
        """
        mock_api.return_value = self.off_response

        ingredient = Ingredient.fetch_ingredient_from_off('1234')

        self.assertEqual(ingredient.name, 'Foo with chocolate')
        self.assertEqual(ingredient.code, '1234')
        self.assertEqual(ingredient.energy, 120)
        self.assertEqual(ingredient.protein, 10)
        self.assertEqual(ingredient.carbohydrates, 20)
        self.assertEqual(ingredient.fat, 40)
        self.assertEqual(ingredient.fat_saturated, 11)
        self.assertEqual(ingredient.sodium, 5)
        self.assertEqual(ingredient.fiber, None)
        self.assertEqual(ingredient.brand, 'The bar company')
        self.assertEqual(ingredient.license_author, 'open food facts, MrX')

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_success_long_name(self, mock_api):
        """
        Tests creating an ingredient from OFF - name gets truncated
        """
        self.off_response['product_name'] = """
        The Shiba Inu (柴犬, Japanese: [ɕiba inɯ]) is a breed of hunting dog from Japan. A
        small-to-medium breed, it is the smallest of the six original and distinct spitz
        breeds of dog native to Japan.[1] Its name literally translates to "brushwood dog",
        as it is used to flush game."""
        mock_api.return_value = self.off_response

        ingredient = Ingredient.fetch_ingredient_from_off('1234')
        self.assertEqual(len(ingredient.name), 200)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_key_missing_1(self, mock_api):
        """
        Tests creating an ingredient from OFF - missing key in nutriments
        """
        del self.off_response['nutriments']['energy-kcal_100g']
        mock_api.return_value = self.off_response

        ingredient = Ingredient.fetch_ingredient_from_off('1234')
        self.assertIsNone(ingredient)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_key_missing_2(self, mock_api):
        """
        Tests creating an ingredient from OFF - missing name
        """
        del self.off_response['product_name']
        mock_api.return_value = self.off_response

        ingredient = Ingredient.fetch_ingredient_from_off('1234')
        self.assertIsNone(ingredient)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_no_results(self, mock_api):
        """
        Tests creating an ingredient from OFF
        """
        mock_api.return_value = self.off_response_no_results

        ingredient = Ingredient.fetch_ingredient_from_off('1234')
        self.assertIsNone(ingredient)


class IngredientApiCodeSearch(BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/ingredient/'

    @patch('wger.nutrition.models.Ingredient.fetch_ingredient_from_off')
    def test_search_existing_code(self, mock_fetch_from_off):
        """
        Test that when a code already exists, no off sync happens
        """
        response = self.client.get(self.url + '?code=1234567890987654321')
        mock_fetch_from_off.assert_not_called()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    @patch('wger.nutrition.models.Ingredient.fetch_ingredient_from_off')
    def test_search_new_code(self, mock_fetch_from_off):
        """
        Test that when a code isn't present, it will be fetched
        """
        response = self.client.get(self.url + '?code=122333444455555666666')
        mock_fetch_from_off.assert_called_with('122333444455555666666')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
