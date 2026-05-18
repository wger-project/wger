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
from unittest.mock import (
    MagicMock,
    patch,
)

# Django
from django.test import SimpleTestCase
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.models import (
    Language,
    License,
)
from wger.core.tests import api_base_test
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import (
    BaseTestCase,
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
)
from wger.nutrition.api.views import (
    IngredientSyncViewSet,
    IngredientViewSet,
)
from wger.nutrition.extract_info.off import extract_info_from_off
from wger.nutrition.models import (
    Ingredient,
    IngredientWeightUnit,
    Meal,
    Source,
)
from wger.nutrition.models.image import Image
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
        Test that the creation date is correctly set
        """
        if self.current_user == 'admin':
            ingredient = Ingredient.objects.get(pk=self.pk_after)
            self.assertEqual(
                ingredient.created.replace(microsecond=0),
                datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0),
            )


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

    @patch('wger.nutrition.models.Ingredient.sync_serving_unit_from_off_if_missing')
    def test_ingredient_detail_does_not_triggers_lazy_serving_sync(self, mock_sync: MagicMock):
        response = self.client.get(reverse('nutrition:ingredient:view', kwargs={'pk': 6}))

        self.assertEqual(response.status_code, 200)
        mock_sync.assert_not_called()


class IngredientSearchTestCase(WgerTestCase):
    """
    Tests the ingredient search functions
    """

    def search_ingredient_en(self):
        """
        Helper function - Searches in English
        """

        response = self.client.get(
            reverse('api-ingredientinfo-list'),
            {'name__search': 'test', 'language__code': 'en'},
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf8'))

        self.assertEqual(result['count'], 2)

        ingredient_1 = result['results'][0]
        self.assertEqual(ingredient_1['id'], 2)
        self.assertEqual(ingredient_1['name'], 'Ingredient, test, 2, organic, raw')
        self.assertEqual(ingredient_1['uuid'], '44dc5966-73a2-4df7-8b15-f6d37a8990d9')
        self.assertEqual(ingredient_1['language']['id'], 2)
        self.assertEqual(ingredient_1['image'], None)
        self.assertEqual(ingredient_1['thumbnails'], None)

        ingredient_2 = result['results'][1]
        self.assertEqual(ingredient_2['id'], 1)
        self.assertEqual(ingredient_2['name'], 'Test ingredient 1')
        self.assertEqual(ingredient_2['uuid'], '7908c204-907f-4b1e-ad4e-f482e9769ade')
        self.assertEqual(ingredient_2['language']['id'], 2)
        self.assertEqual(ingredient_2['image'], None)
        self.assertEqual(ingredient_2['thumbnails'], None)

    def search_ingredient_de(self):
        """
        Helper function - Searches in German
        """

        response = self.client.get(
            reverse('api-ingredientinfo-list'),
            {'name__search': 'test', 'language__code': 'de'},
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf8'))

        self.assertEqual(result['count'], 1)

        ingredient_1 = result['results'][0]
        self.assertEqual(ingredient_1['id'], 6)
        self.assertEqual(ingredient_1['name'], 'Testzutat 123')
        self.assertEqual(ingredient_1['uuid'], 'dfc5c622-027b-4f17-8141-dadd1ce7e3f1')
        self.assertEqual(ingredient_1['language']['id'], 1)
        self.assertEqual(ingredient_1['image'], None)
        self.assertEqual(ingredient_1['thumbnails'], None)

    def test_search_ingredient_anonymous(self):
        """
        Test searching for an ingredient by an anonymous user
        """

        self.search_ingredient_en()
        self.search_ingredient_de()

    def test_search_ingredient_logged_in(self):
        """
        Test searching for an ingredient by a logged-in user
        """

        self.user_login('test')
        self.search_ingredient_en()
        self.search_ingredient_de()


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
                'sodium': 1.22427,
                'energy': 392.48,
                # 'energy_kilojoule': '1642.14',
                'fat': 18.2637,
                'carbohydrates_sugar': None,
                'fat_saturated': 7.23412,
                'fiber': None,
                'protein': 57.1549,
                'carbohydrates': 0.27875,
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


class IngredientApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the ingredient API resource
    """

    pk = 4
    resource = Ingredient
    private_resource = False
    overview_cached = False
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
            'name': 'Foo with chocolate',
            'product_name': 'Foo with chocolate',
            'generic_name': 'Foo with chocolate, 250g package',
            'brands': 'The bar company',
            'editors_tags': ['open food facts', 'MrX'],
            'ingredients_analysis_tags': [
                'en:palm-oil-free',
                'en:vegan',
                'en:vegetarian',
            ],
            'nutriments': {
                'energy-kcal_100g': 600,
                'proteins_100g': 10,
                'carbohydrates_100g': 30,
                'sugars_100g': 20,
                'fat_100g': 40,
                'saturated-fat_100g': 11,
                'sodium_100g': 5,
                'fiber_100g': None,
            },
        }

        self.off_response_no_results = None

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_success(self, mock_api: MagicMock):
        """
        Tests creating an ingredient from OFF
        """
        mock_api.return_value = self.off_response

        ingredient = Ingredient.fetch_ingredient_from_off('1234')

        self.assertEqual(ingredient.name, 'Foo with chocolate')
        self.assertEqual(ingredient.code, '1234')
        self.assertEqual(ingredient.energy, 600)
        self.assertEqual(ingredient.protein, 10)
        self.assertEqual(ingredient.carbohydrates, 30)
        self.assertEqual(ingredient.fat, 40)
        self.assertEqual(ingredient.fat_saturated, 11)
        self.assertEqual(ingredient.sodium, 5)
        self.assertEqual(ingredient.fiber, None)
        self.assertEqual(ingredient.brand, 'The bar company')
        self.assertEqual(ingredient.license_author, 'open food facts, MrX')
        self.assertTrue(ingredient.is_vegan)
        self.assertTrue(ingredient.is_vegetarian)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_updates_existing_serving_unit(self, mock_api: MagicMock):
        self.off_response['serving_size'] = '2 biscuits (30 g)'
        mock_api.return_value = self.off_response
        ingredient = Ingredient.fetch_ingredient_from_off('1234')

        self.off_response['serving_size'] = '2 biscuits (25 g)'
        ingredient.update_or_create_serving_unit_from_off(
            extract_info_from_off(self.off_response, ingredient.language_id)
        )

        ingredient_unit = IngredientWeightUnit.objects.get(
            ingredient=ingredient, name='1 Portion (2 biscuits)'
        )
        self.assertEqual(ingredient_unit.gram, 25)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_reimport_same_gram_different_name_does_not_duplicate(self, mock_api: MagicMock):
        """
        When OFF changes the serving_size text but the gram value stays,
        the existing unit is reused (matched by gram) instead of creating a duplicate.
        """
        self.off_response['serving_size'] = '2 biscuits (30 g)'
        mock_api.return_value = self.off_response
        ingredient = Ingredient.fetch_ingredient_from_off('1234')

        self.off_response['serving_size'] = '3 biscuits (30 g)'
        ingredient.update_or_create_serving_unit_from_off(
            extract_info_from_off(self.off_response, ingredient.language_id)
        )

        units = IngredientWeightUnit.objects.filter(ingredient=ingredient)
        self.assertEqual(units.count(), 1)
        self.assertEqual(units.first().name, '1 Portion (3 biscuits)')
        self.assertEqual(units.first().gram, 30)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_success_long_name(self, mock_api: MagicMock):
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
    def test_fetch_from_off_key_missing_1(self, mock_api: MagicMock):
        """
        Tests creating an ingredient from OFF - missing key in nutriments
        """
        del self.off_response['nutriments']['energy-kcal_100g']
        mock_api.return_value = self.off_response

        ingredient = Ingredient.fetch_ingredient_from_off('1234')
        self.assertIsNone(ingredient)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_key_missing_2(self, mock_api: MagicMock):
        """
        Tests creating an ingredient from OFF - missing name
        """
        del self.off_response['product_name']
        mock_api.return_value = self.off_response

        ingredient = Ingredient.fetch_ingredient_from_off('1234')
        self.assertIsNone(ingredient)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_no_results(self, mock_api: MagicMock):
        """
        Tests creating an ingredient from OFF
        """
        mock_api.return_value = self.off_response_no_results

        ingredient = Ingredient.fetch_ingredient_from_off('1234')
        self.assertIsNone(ingredient)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_sync_serving_unit_from_off_if_missing_creates_unit(self, mock_api: MagicMock):
        mock_api.return_value = {
            **self.off_response,
            'serving_size': '2 biscuits (30 g)',
        }
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.source_name = Source.OPEN_FOOD_FACTS.value
        ingredient.code = '1234'
        ingredient.save(update_fields=['source_name', 'code'])
        ingredient.ingredientweightunit_set.all().delete()

        created, updated = ingredient.sync_serving_unit_from_off_if_missing()

        self.assertEqual((created, updated), (True, False))
        self.assertEqual(ingredient.ingredientweightunit_set.count(), 1)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_sync_serving_unit_from_off_if_missing_skips_existing_units(self, mock_api: MagicMock):
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.source_name = Source.OPEN_FOOD_FACTS.value
        ingredient.code = '1234'
        ingredient.save(update_fields=['source_name', 'code'])
        ingredient.ingredientweightunit_set.get_or_create(
            name='Cup',
            defaults={'gram': 15},
        )

        created, updated = ingredient.sync_serving_unit_from_off_if_missing()

        self.assertEqual((created, updated), (False, False))
        mock_api.assert_not_called()

    @patch('openfoodfacts.api.ProductResource.get')
    def test_sync_serving_unit_from_off_if_missing_skips_non_off_source(self, mock_api: MagicMock):
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.source_name = Source.USDA.value
        ingredient.code = '1234'
        ingredient.save(update_fields=['source_name', 'code'])
        ingredient.ingredientweightunit_set.all().delete()

        created, updated = ingredient.sync_serving_unit_from_off_if_missing()

        self.assertEqual((created, updated), (False, False))
        mock_api.assert_not_called()

    @patch('openfoodfacts.api.ProductResource.get')
    def test_sync_serving_unit_from_off_if_missing_skips_missing_code(self, mock_api: MagicMock):
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.source_name = Source.OPEN_FOOD_FACTS.value
        ingredient.code = ''
        ingredient.save(update_fields=['source_name', 'code'])
        ingredient.ingredientweightunit_set.all().delete()

        created, updated = ingredient.sync_serving_unit_from_off_if_missing()

        self.assertEqual((created, updated), (False, False))
        mock_api.assert_not_called()

    @patch('openfoodfacts.api.ProductResource.get')
    def test_sync_serving_unit_from_off_if_missing_handles_off_fetch_failure(
        self, mock_api: MagicMock
    ):
        mock_api.return_value = None
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.source_name = Source.OPEN_FOOD_FACTS.value
        ingredient.code = '1234'
        ingredient.save(update_fields=['source_name', 'code'])
        ingredient.ingredientweightunit_set.all().delete()

        created, updated = ingredient.sync_serving_unit_from_off_if_missing()

        self.assertEqual((created, updated), (False, False))
        self.assertEqual(ingredient.ingredientweightunit_set.count(), 0)

    @patch('openfoodfacts.api.ProductResource.get')
    def test_fetch_from_off_does_not_create_unit_for_non_derivable_serving_size(self, mock_api):
        self.off_response['serving_size'] = '2 tbsp'
        mock_api.return_value = self.off_response

        ingredient = Ingredient.fetch_ingredient_from_off('1234')

        self.assertIsNotNone(ingredient)
        self.assertEqual(ingredient.ingredientweightunit_set.count(), 0)


class IngredientInfoLazyServingUnitSyncApiTestCase(WgerTestCase):
    @patch('wger.nutrition.models.Ingredient.sync_serving_unit_from_off_if_missing')
    def test_detail_triggers_lazy_sync(self, mock_sync: MagicMock):
        self.client.get(reverse('api-ingredientinfo-detail', kwargs={'pk': 1}))
        mock_sync.assert_not_called()

    @patch('wger.nutrition.models.Ingredient.sync_serving_unit_from_off_if_missing')
    def test_list_does_not_trigger_lazy_sync(self, mock_sync):
        self.client.get(reverse('api-ingredientinfo-list'))
        mock_sync.assert_not_called()


class IngredientApiCodeSearch(BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/ingredient/'

    @patch('wger.nutrition.models.Ingredient.fetch_ingredient_from_off')
    def test_search_existing_code(self, mock_fetch_from_off: MagicMock):
        """
        Test that when a code already exists, no off sync happens
        """
        response = self.client.get(self.url + '?code=1234567890987654321')
        mock_fetch_from_off.assert_not_called()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    @patch('wger.nutrition.models.Ingredient.fetch_ingredient_from_off')
    def test_search_new_code(self, mock_fetch_from_off: MagicMock):
        """
        Test that when a code isn't present, it will be fetched
        """
        response = self.client.get(self.url + '?code=122333444455555666666')
        mock_fetch_from_off.assert_called_with('122333444455555666666')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class ImageFromJsonSimpleTests(SimpleTestCase):
    def test_from_json_sets_uuid_size_and_license_when_generate_uuid_false(self):
        json_data = {
            'uuid': '123e4567-e89b-12d3-a456-426614174000',
            'license_title': 'CC0',
            'license_object_url': 'https://license.example/',
            'license_author': 'Author Name',
            'license_author_url': 'https://author.example/',
            'license_derivative_source_url': 'https://source.example/',
            'size': 12345,
        }

        img = Image.from_json(
            connect_to=None,
            retrieved_image=None,
            json_data=json_data,
            generate_uuid=False,
            save_to_db=False,
        )

        self.assertIsInstance(img, Image)
        self.assertEqual(str(img.uuid), json_data['uuid'])
        self.assertEqual(img.size, 12345)
        self.assertEqual(img.license_title, json_data['license_title'])

    def test_from_json_generate_uuid_true_uses_model_default_uuid(self):
        json_data = {
            'uuid': '123e4567-e89b-12d3-a456-426614174001',
            'license_title': 'CC0',
            'license_object_url': 'https://license.example/',
            'license_author': 'Author Name',
            'license_author_url': 'https://author.example/',
            'license_derivative_source_url': 'https://source.example/',
            'size': 54321,
        }

        img = Image.from_json(
            connect_to=None,
            retrieved_image=None,
            json_data=json_data,
            generate_uuid=True,
            save_to_db=False,
        )

        self.assertIsInstance(img, Image)
        self.assertNotEqual(str(img.uuid), json_data['uuid'])
        self.assertEqual(img.size, 54321)


class AttributionLinkTestCase(SimpleTestCase):
    """
    Tests that AbstractLicenseModel.attribution_link only emits http(s) links.

    Image is used as a representative concrete subclass; attribution_link is
    defined once on the shared AbstractLicenseModel.
    """

    def test_javascript_scheme_is_not_rendered_as_link(self):
        """A javascript: URL must never end up inside an href attribute."""

        image = Image(
            license=License(pk=1, short_name='CC', url='javascript:alert(1)'),
            license_title='A photo',
            license_author='Some Author',
            license_object_url='javascript:alert(2)',
            license_author_url='javascript:alert(document.cookie)',
            license_derivative_source_url='javascript:void(0)',
        )

        result = image.attribution_link

        self.assertNotIn('javascript:', result)
        # The text content is still shown, just no longer linked
        self.assertIn('A photo', result)
        self.assertIn('Some Author', result)

    def test_http_urls_are_rendered_as_links(self):
        """Valid http(s) URLs are still emitted as links."""

        image = Image(
            license=License(pk=1, short_name='CC', url='https://example.com/license'),
            license_title='A photo',
            license_author='Some Author',
            license_object_url='https://example.com/photo',
            license_author_url='http://example.com/author',
        )

        result = image.attribution_link

        self.assertIn('href="https://example.com/photo"', result)
        self.assertIn('href="http://example.com/author"', result)
        self.assertIn('href="https://example.com/license"', result)


class IngredientThrottleScopeTestCase(WgerTestCase):
    """
    Tests that ingredient viewsets are wired up with the right throttle scopes.

    We don't exercise the rate limits themselves (the rates are config) — we
    just assert that scopes are picked correctly per action so accidental
    refactors can't silently strip throttling.
    """

    def test_ingredient_list_uses_list_scope(self):
        view = IngredientViewSet()
        view.action = 'list'
        view.get_throttles()
        self.assertEqual(view.throttle_scope, 'ingredient_list')

    def test_ingredient_detail_uses_detail_scope(self):
        view = IngredientViewSet()
        view.action = 'retrieve'
        view.get_throttles()
        self.assertEqual(view.throttle_scope, 'ingredient_detail')

    def test_ingredient_sync_uses_sync_scope(self):
        self.assertEqual(IngredientSyncViewSet.throttle_scope, 'ingredient_sync')


class IngredientSyncViewSetTestCase(WgerTestCase):
    """
    Tests for the /api/v2/ingredient-sync endpoint.
    """

    url = reverse('api-ingredient-sync-list')

    def test_list_returns_cursor_pagination_shape(self):
        """The response has `next`/`previous`, but no `count`."""

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertNotIn('count', response.data)

    def test_list_paginates_through_all_ingredients(self):
        """Following `next` returns disjoint pages that together cover all rows."""

        total = Ingredient.objects.count()
        self.assertGreater(total, 0, 'Fixture must contain ingredients')

        seen_ids = []
        url = self.url + '?page_size=5'
        while url:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            seen_ids.extend(item['id'] for item in response.data['results'])
            url = response.data['next']

        # No duplicates and every ingredient seen exactly once.
        self.assertEqual(len(seen_ids), len(set(seen_ids)))
        self.assertEqual(set(seen_ids), set(Ingredient.objects.values_list('id', flat=True)))

    def test_page_size_query_param_is_capped(self):
        """`?page_size=` is honored but capped at `max_page_size`."""

        # Way above max_page_size=1000 — must be capped, not error
        response = self.client.get(self.url + '?page_size=999999')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 1000)

    def test_filterset_supports_incremental_sync(self):
        """`last_update__gt` filter narrows the result set for incremental syncs."""

        # Pick a timestamp newer than all fixture rows -> empty result
        future = '2999-01-01T00:00:00Z'
        response = self.client.get(f'{self.url}?last_update__gt={future}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])
        self.assertIsNone(response.data['next'])
