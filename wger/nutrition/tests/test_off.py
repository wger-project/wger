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

# Django
from django.test import SimpleTestCase

# wger
from wger.nutrition.dataclasses import IngredientData
from wger.nutrition.extract_info.off import extract_info_from_off
from wger.utils.constants import ODBL_LICENSE_ID


class ExtractInfoFromOffTestCase(SimpleTestCase):
    """
    Test the extract_info_from_off function
    """

    off_data1 = {}

    def setUp(self):
        self.off_data1 = {
            'code': '1234',
            'lang': 'de',
            'product_name': 'Foo with chocolate',
            'generic_name': 'Foo with chocolate, 250g package',
            'brands': 'The bar company',
            'editors_tags': ['open food facts', 'MrX'],
            'ingredients_analysis_tags': [
                'en:palm-oil-free',
                'en:vegan',
                'en:vegetarian',
            ],
            'nutrition_grades': 'c',
            'nutriments': {
                'energy-kcal_100g': 120,
                'proteins_100g': 10,
                'carbohydrates_100g': 20,
                'sugars_100g': 30,
                'fat_100g': 40,
                'saturated-fat_100g': 11,
                'sodium_100g': 5,
                'fiber_100g': None,
                'other_stuff': 'is ignored',
            },
        }

    def test_regular_response(self):
        """
        Test that the function can read the regular case
        """
        result = extract_info_from_off(self.off_data1, 1)
        data = IngredientData(
            name='Foo with chocolate',
            remote_id='1234',
            language_id=1,
            energy=120,
            protein=10,
            carbohydrates=20,
            carbohydrates_sugar=30,
            fat=40,
            fat_saturated=11,
            fiber=None,
            sodium=5,
            code='1234',
            source_name='Open Food Facts',
            source_url='https://world.openfoodfacts.org/api/v2/product/1234.json',
            common_name='Foo with chocolate, 250g package',
            brand='The bar company',
            license_id=ODBL_LICENSE_ID,
            license_author='open food facts, MrX',
            license_title='Foo with chocolate',
            license_object_url='https://world.openfoodfacts.org/product/1234/',
            is_vegan=True,
            is_vegetarian=True,
            nutriscore='c',
        )

        self.assertEqual(result, data)

    def test_convert_kj(self):
        """
        If the energy is not available in kcal per 100 g, but is in kj per 100 g,
        we convert it to kcal per 100 g
        """
        del self.off_data1['nutriments']['energy-kcal_100g']
        self.off_data1['nutriments']['energy-kj_100g'] = 120

        result = extract_info_from_off(self.off_data1, 1)

        # 120 / KJ_PER_KCAL
        self.assertAlmostEqual(result.energy, 28.6806, 3)

    def test_no_energy(self):
        """
        No energy available
        """
        del self.off_data1['nutriments']['energy-kcal_100g']

        self.assertRaises(KeyError, extract_info_from_off, self.off_data1, 1)

    def test_no_sugar_or_saturated_fat(self):
        """
        No sugar or saturated fat available
        """
        del self.off_data1['nutriments']['sugars_100g']
        del self.off_data1['nutriments']['saturated-fat_100g']
        result = extract_info_from_off(self.off_data1, 1)

        self.assertEqual(result.carbohydrates_sugar, None)
        self.assertEqual(result.fat_saturated, None)

    def test_vegan_product(self):
        """
        Test that vegan/vegetarian status is correctly extracted
        """
        result = extract_info_from_off(self.off_data1, 1)
        self.assertTrue(result.is_vegan)
        self.assertTrue(result.is_vegetarian)

    def test_non_vegan_product(self):
        """
        Test that non-vegan product is correctly detected
        """
        self.off_data1['ingredients_analysis_tags'] = [
            'en:palm-oil-free',
            'en:non-vegan',
            'en:vegetarian',
        ]
        result = extract_info_from_off(self.off_data1, 1)
        self.assertFalse(result.is_vegan)
        self.assertTrue(result.is_vegetarian)

    def test_non_vegetarian_product(self):
        """
        Test that non-vegetarian product is correctly detected
        """
        self.off_data1['ingredients_analysis_tags'] = [
            'en:palm-oil-free',
            'en:non-vegan',
            'en:non-vegetarian',
        ]
        result = extract_info_from_off(self.off_data1, 1)
        self.assertFalse(result.is_vegan)
        self.assertFalse(result.is_vegetarian)

    def test_unknown_vegan_status(self):
        """
        Test that unknown vegan status returns None
        """
        self.off_data1['ingredients_analysis_tags'] = [
            'en:palm-oil-free',
            'en:vegan-status-unknown',
            'en:vegetarian-status-unknown',
        ]
        result = extract_info_from_off(self.off_data1, 1)
        self.assertIsNone(result.is_vegan)
        self.assertIsNone(result.is_vegetarian)

    def test_no_analysis_tags(self):
        """
        Test that missing ingredients_analysis_tags returns None
        """
        del self.off_data1['ingredients_analysis_tags']
        result = extract_info_from_off(self.off_data1, 1)
        self.assertIsNone(result.is_vegan)
        self.assertIsNone(result.is_vegetarian)

    def test_nutriscore_extracted(self):
        """
        Test that nutriscore is correctly extracted
        """
        result = extract_info_from_off(self.off_data1, 1)
        self.assertEqual(result.nutriscore, 'c')

    def test_nutriscore_missing(self):
        """
        Test that missing nutrition_grades returns None
        """
        del self.off_data1['nutrition_grades']
        result = extract_info_from_off(self.off_data1, 1)
        self.assertIsNone(result.nutriscore)

    def test_nutriscore_invalid(self):
        """
        Test that invalid nutrition_grades value returns None
        """
        self.off_data1['nutrition_grades'] = 'z'
        result = extract_info_from_off(self.off_data1, 1)
        self.assertIsNone(result.nutriscore)

    def test_ingredient_clean_name(self):
        data = IngredientData(
            name='Stonebaked Pizza &quot;the amer\x96ican \x99pepperoni&quot;',
            remote_id='1234',
            language_id=1,
            energy=120,
            protein=10,
            carbohydrates=20,
            carbohydrates_sugar=30,
            fat=40,
            fat_saturated=11,
            fiber=None,
            sodium=5,
            code='1234',
            source_name='Open Food Facts',
            source_url='https://world.openfoodfacts.org/api/v2/product/1234.json',
            common_name='',
            brand='The bar company',
            license_id=ODBL_LICENSE_ID,
            license_author='open food facts, MrX',
            license_title='Foo with chocolate',
            license_object_url='https://world.openfoodfacts.org/product/1234/',
        )
        data.clean_name()
        self.assertEqual(data.name, 'Stonebaked Pizza "the american pepperoni"')

    def test_serving_size_parsed(self):
        self.off_data1['serving_size'] = '2 biscuits (30 g)'

        result = extract_info_from_off(self.off_data1, 1)

        self.assertEqual(result.serving_size_gram, 30)
        self.assertEqual(result.serving_size_unit, 'biscuits')
        self.assertEqual(result.serving_size_amount, 2)

    def test_serving_size_only_grams(self):
        self.off_data1['serving_size'] = '30 g'

        result = extract_info_from_off(self.off_data1, 1)

        self.assertEqual(result.serving_size_gram, 30)
        self.assertEqual(result.serving_size_unit, 'Serving')
        self.assertEqual(result.serving_size_amount, 1)

    def test_serving_size_volume_with_gram_equivalent(self):
        self.off_data1['serving_size'] = '200 ml (206 g)'

        result = extract_info_from_off(self.off_data1, 1)

        self.assertEqual(result.serving_size_gram, 206)
        self.assertEqual(result.serving_size_unit, 'ml')
        self.assertEqual(result.serving_size_amount, 200)

    def test_serving_size_without_mass_is_parsed(self):
        self.off_data1['serving_size'] = '200 ml'

        result = extract_info_from_off(self.off_data1, 1)

        self.assertIsNone(result.serving_size_gram)
        self.assertEqual(result.serving_size_unit, 'ml')
        self.assertEqual(result.serving_size_amount, 200)
