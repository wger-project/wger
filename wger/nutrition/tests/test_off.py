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
from copy import deepcopy
from decimal import Decimal

# Django
from django.test import SimpleTestCase
from django.utils import translation
from django.utils.translation import gettext

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
                'energy-kcal_100g': 600,
                'proteins_100g': 10,
                'carbohydrates_100g': 30,
                'sugars_100g': 20,
                'fat_100g': 40,
                'saturated-fat_100g': 11,
                'sodium_100g': 5,
                'fiber_100g': None,
                'other_stuff': 'is ignored',
            },
            'serving_size': '',
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
            energy=600,
            protein=10,
            carbohydrates=30,
            carbohydrates_sugar=20,
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
        self.off_data1['nutriments']['energy-kj_100g'] = 2510.4

        result = extract_info_from_off(self.off_data1, 1)

        # 120 / KJ_PER_KCAL
        self.assertAlmostEqual(result.energy, 600, 3)

    def test_no_energy(self):
        """
        No energy available
        """
        del self.off_data1['nutriments']['energy-kcal_100g']

        self.assertRaises(KeyError, extract_info_from_off, self.off_data1, 1)

    def test_product_name_fallback_to_english(self):
        """
        If 'product_name' is missing, fall back to 'product_name_en'
        """

        del self.off_data1['product_name']
        self.off_data1['product_name_en'] = 'Foo English'

        result = extract_info_from_off(self.off_data1, 1)
        self.assertEqual(result.name, 'Foo English')

    def test_product_name_prefers_request_language(self):
        """
        If 'product_name' is missing, prefer the localized name matching 'lang'
        over the English fallback
        """

        del self.off_data1['product_name']
        self.off_data1['lang'] = 'de'
        self.off_data1['product_name_de'] = 'Foo Deutsch'
        self.off_data1['product_name_en'] = 'Foo English'
        self.off_data1['product_name_fr'] = 'Foo Français'

        result = extract_info_from_off(self.off_data1, 1)
        self.assertEqual(result.name, 'Foo Deutsch')

    def test_product_name_fallback_to_any_localized(self):
        """
        If neither 'product_name' nor 'product_name_en' is set, fall back to
        any localized 'product_name_*' key
        """

        del self.off_data1['product_name']
        self.off_data1['product_name_de'] = 'Foo Deutsch'

        result = extract_info_from_off(self.off_data1, 1)
        self.assertEqual(result.name, 'Foo Deutsch')

    def test_no_product_name_at_all(self):
        """
        If no product name is present, raise KeyError
        """

        del self.off_data1['product_name']

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
        # The fallback unit is translated into the product's language, so pin
        # it to English to be independent of compiled locale files.
        self.off_data1['lang'] = 'en'
        self.off_data1['serving_size'] = '30 g'

        result = extract_info_from_off(self.off_data1, 1)

        self.assertEqual(result.serving_size_gram, 30)
        self.assertEqual(result.serving_size_unit, 'Serving')
        self.assertEqual(result.serving_size_amount, 1)

    def test_serving_size_fallback_unit_uses_product_language(self):
        """
        The fallback unit is translated into the product's language
        """
        self.off_data1['serving_size'] = '30 g'  # lang is already 'de' in the fixture

        result = extract_info_from_off(self.off_data1, 1)

        # Compute the expected value through the same catalog so the test works
        # with and without compiled locale files
        with translation.override('de'):
            self.assertEqual(result.serving_size_unit, gettext('Serving'))

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

    def per_serving_product(self) -> dict:
        product = deepcopy(self.off_data1)
        product.update(serving_size='20 g', serving_quantity='20', serving_quantity_unit='g')
        product['nutriments'] = {
            'energy-kcal_serving': 120,
            'proteins_serving': 2,
            'carbohydrates_serving': 6,
            'sugars_serving': 4,
            'fat_serving': 8,
            'saturated-fat_serving': 2.2,
            'sodium_serving': 1,
            'fiber_serving': 0.2,
        }
        return product

    def test_missing_protein_uses_per_serving_value(self):
        """Missing protein is derived using an explicit gram weight in a legacy label."""
        self.off_data1.update(serving_size='20 g', serving_quantity=20)
        self.off_data1['nutriments'].update(proteins_serving=4)
        self.off_data1['nutriments']['energy-kcal_100g'] = 560
        del self.off_data1['nutriments']['proteins_100g']

        result = extract_info_from_off(self.off_data1, 1)

        self.assertEqual(result.protein, 20)

    def test_per_serving_nutrients_are_converted(self):
        product = self.per_serving_product()
        original = deepcopy(product)

        result = extract_info_from_off(product, 1)

        for field, expected in {
            'energy': 600,
            'protein': 10,
            'carbohydrates': 30,
            'carbohydrates_sugar': 20,
            'fat': 40,
            'fat_saturated': 11,
            'sodium': 5,
            'fiber': 1,
        }.items():
            with self.subTest(field=field):
                self.assertAlmostEqual(getattr(result, field), expected)
        self.assertEqual(product, original)

    def test_existing_per_100g_values_take_precedence(self):
        product = self.per_serving_product()
        product['nutriments'].update(proteins_100g=15, sugars_100g=0)

        result = extract_info_from_off(product, 1)

        self.assertEqual(result.protein, 15)
        self.assertEqual(result.carbohydrates_sugar, 0)
        self.assertEqual(result.carbohydrates, 30)

    def test_existing_zero_energy_and_macros_are_preserved(self):
        product = self.per_serving_product()
        for nutrient in ('energy-kcal', 'proteins', 'carbohydrates', 'fat', 'saturated-fat'):
            product['nutriments'][f'{nutrient}_100g'] = 0
        product['nutriments'].update(sugars_100g=0, sodium_100g=0, fiber_100g=0)

        result = extract_info_from_off(product, 1)

        self.assertEqual(
            (result.energy, result.protein, result.carbohydrates, result.fat), (0,) * 4
        )

    def test_per_100g_kj_takes_precedence_over_per_serving_kcal(self):
        del self.off_data1['nutriments']['energy-kcal_100g']
        self.off_data1['nutriments']['energy-kj_100g'] = 2510.4
        self.off_data1['nutriments']['energy-kcal_serving'] = 1
        self.off_data1.update(serving_quantity=20, serving_quantity_unit='g')

        result = extract_info_from_off(self.off_data1, 1)

        self.assertAlmostEqual(result.energy, 600)

    def test_per_serving_energy_in_kj_is_converted(self):
        product = self.per_serving_product()
        del product['nutriments']['energy-kcal_serving']
        product['nutriments']['energy-kj_serving'] = 502.08

        result = extract_info_from_off(product, 1)

        self.assertAlmostEqual(result.energy, 600)

    def test_null_per_100g_values_can_use_the_fallback(self):
        product = self.per_serving_product()
        product['nutriments'].update(proteins_100g=None, sodium_100g=None)
        product['nutriments']['energy-kcal_100g'] = None

        result = extract_info_from_off(product, 1)

        self.assertEqual(result.protein, 10)
        self.assertEqual(result.sodium, 5)
        self.assertEqual(result.energy, 600)

    def test_missing_optional_serving_nutrients_remain_none(self):
        product = self.per_serving_product()
        for nutrient in ('sugars', 'saturated-fat', 'sodium', 'fiber'):
            del product['nutriments'][f'{nutrient}_serving']

        result = extract_info_from_off(product, 1)

        for field in ('carbohydrates_sugar', 'fat_saturated', 'sodium', 'fiber'):
            with self.subTest(field=field):
                self.assertIsNone(getattr(result, field))

    def test_invalid_normalized_serving_weights_cannot_fill_missing_nutrients(self):
        for quantity in (None, '', 0, -20, 'NaN', 'Infinity', True, [], {}, 'twenty'):
            with self.subTest(quantity=quantity):
                product = self.per_serving_product()
                product['serving_quantity'] = quantity
                with self.assertRaisesRegex(KeyError, 'Missing required nutrition key'):
                    extract_info_from_off(product, 1)

    def test_volume_or_unknown_units_are_not_assumed_to_be_grams(self):
        for unit in ('ml', 'oz', 'unknown'):
            with self.subTest(unit=unit):
                product = self.per_serving_product()
                product['serving_quantity_unit'] = unit
                product['serving_size'] = f'20 {unit}'
                with self.assertRaisesRegex(KeyError, 'Missing required nutrition key'):
                    extract_info_from_off(product, 1)

    def test_volume_serving_with_explicit_gram_equivalent_is_supported(self):
        product = self.per_serving_product()
        product.update(
            serving_quantity='18', serving_quantity_unit='ml', serving_size='18 ml (20 g)'
        )

        result = extract_info_from_off(product, 1)

        self.assertEqual(result.protein, 10)
        self.assertEqual(result.serving_size_gram, 20)

    def test_legacy_serving_text_requires_an_explicit_positive_mass(self):
        for serving in (
            '',
            '1 serving',
            '20 ml',
            '0 g',
            '-20 g',
            '\u221220 g',
            '1e2 g',
            '1/2 g',
            '2x20g',
        ):
            with self.subTest(serving=serving):
                product = self.per_serving_product()
                product.pop('serving_quantity_unit')
                product['serving_size'] = serving
                with self.assertRaisesRegex(KeyError, 'Missing required nutrition key'):
                    extract_info_from_off(product, 1)

    def test_legacy_mass_units_and_parentheses_are_supported(self):
        for serving in ('20 g', '2 biscuits (20 g)', '0.02 kg', '20000 mg', '20,0 g'):
            with self.subTest(serving=serving):
                product = self.per_serving_product()
                product.pop('serving_quantity_unit')
                product['serving_size'] = serving

                result = extract_info_from_off(product, 1)

                self.assertEqual(result.protein, 10)

    def test_existing_compact_mass_label_parsing_is_preserved(self):
        self.off_data1['serving_size'] = '2x30g'

        result = extract_info_from_off(self.off_data1, 1)

        self.assertEqual(result.serving_size_gram, 30)

    def test_fractional_serving_mass_is_not_rounded_for_nutrients(self):
        for unit in ('g', None):
            with self.subTest(normalized_unit=unit):
                product = self.per_serving_product()
                product.update(serving_quantity='5.1', serving_size='5.1 g')
                if unit is None:
                    product.pop('serving_quantity_unit')
                product['nutriments'] = {
                    'energy-kcal_serving': 30.6,
                    'proteins_serving': 0.51,
                    'carbohydrates_serving': 1.53,
                    'fat_serving': 2.04,
                }

                result = extract_info_from_off(product, 1)

                self.assertAlmostEqual(result.protein, 10)
                self.assertAlmostEqual(result.energy, 600)

    def test_per_serving_conversion_requires_at_least_five_grams(self):
        for unit in ('g', None, 'ml'):
            for mass in (0.5, 4.999, 5, 5.001):
                with self.subTest(normalized_unit=unit, mass=mass):
                    product = self.per_serving_product()
                    product.update(serving_quantity=mass, serving_size=f'{mass} g')
                    if unit is None:
                        product.pop('serving_quantity_unit')
                    elif unit == 'ml':
                        product.update(
                            serving_quantity=20,
                            serving_quantity_unit='ml',
                            serving_size=f'20 ml ({mass} g)',
                        )
                    product['nutriments'] = {
                        'energy-kcal_serving': 3,
                        'proteins_serving': 0.05,
                        'carbohydrates_serving': 0.15,
                        'fat_serving': 0.2,
                    }

                    if mass < 5:
                        with self.assertRaisesRegex(KeyError, 'Missing required nutrition key'):
                            extract_info_from_off(product, 1)
                    else:
                        result = extract_info_from_off(product, 1)
                        self.assertAlmostEqual(result.protein, 0.05 / mass * 100)

    def test_small_servings_preserve_existing_per_100g_data(self):
        self.off_data1.update(serving_quantity=0.5, serving_quantity_unit='g', serving_size='0.5 g')
        self.off_data1['nutriments'].update(proteins_serving=0.1, fiber_serving=0.005)

        result = extract_info_from_off(self.off_data1, 1)

        self.assertEqual(result.protein, 10)
        self.assertEqual(result.energy, 600)
        self.assertIsNone(result.fiber)

    def test_small_servings_cannot_supply_missing_energy(self):
        self.off_data1.update(serving_quantity=4.999, serving_quantity_unit='g')
        del self.off_data1['nutriments']['energy-kcal_100g']
        self.off_data1['nutriments']['energy-kcal_serving'] = 30

        with self.assertRaisesRegex(KeyError, 'Energy is not available'):
            extract_info_from_off(self.off_data1, 1)

    def test_invalid_per_serving_nutrients_raise_value_error(self):
        for nutrient in ('proteins', 'fiber', 'energy-kcal'):
            for value in (
                -1,
                -5e-324,
                Decimal('-1e-10000'),
                float('nan'),
                float('inf'),
                Decimal('NaN'),
                Decimal('sNaN'),
                10**1000,
                '2',
                True,
                [],
            ):
                with self.subTest(nutrient=nutrient, value=value):
                    product = self.per_serving_product()
                    product['nutriments'][f'{nutrient}_serving'] = value
                    with self.assertRaises(ValueError):
                        extract_info_from_off(product, 1)

    def test_finite_numeric_per_serving_types_are_supported(self):
        for value in (2, 2.0, Decimal('2')):
            with self.subTest(value=value):
                product = self.per_serving_product()
                product['nutriments']['proteins_serving'] = value

                result = extract_info_from_off(product, 1)

                self.assertEqual(result.protein, 10)

    def test_invalid_unused_serving_metadata_does_not_reject_per_100g_data(self):
        self.off_data1.update(serving_quantity='NaN', serving_quantity_unit='g')
        self.off_data1['nutriments']['proteins_serving'] = 'invalid'

        result = extract_info_from_off(self.off_data1, 1)

        self.assertEqual(result.protein, 10)

    def test_converted_values_still_pass_through_sanity_checks(self):
        for nutrient, value, message in (
            ('proteins', 25, 'greater than 100'),
            ('sugars', 7, 'Sugar is greater than carbohydrates'),
            ('saturated-fat', 9, 'Saturated fat is greater than fat'),
            ('energy-kcal', 1, 'does not match the declared energy'),
        ):
            with self.subTest(nutrient=nutrient):
                product = self.per_serving_product()
                product['nutriments'][f'{nutrient}_serving'] = value
                with self.assertRaisesRegex(ValueError, message):
                    extract_info_from_off(product, 1)

    def test_missing_or_prepared_only_nutrients_remain_rejected(self):
        for prepared in (False, True):
            with self.subTest(prepared=prepared):
                product = self.per_serving_product()
                protein = product['nutriments'].pop('proteins_serving')
                if prepared:
                    product['nutriments']['proteins_prepared_serving'] = protein
                with self.assertRaisesRegex(KeyError, 'Missing required nutrition key'):
                    extract_info_from_off(product, 1)
