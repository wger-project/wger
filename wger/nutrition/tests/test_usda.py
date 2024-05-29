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
from wger.nutrition.usda import (
    convert_to_grams,
    extract_info_from_usda,
)
from wger.utils.constants import CC_0_LICENSE_ID


class ExtractInfoFromUSDATestCase(SimpleTestCase):
    """
    Test the extract_info_from_usda function
    """

    usda_data1 = {}

    def setUp(self):
        self.usda_data1 = {
            'foodClass': 'FinalFood',
            'description': 'FOO WITH CHOCOLATE',
            'foodNutrients': [
                {
                    'type': 'FoodNutrient',
                    'id': 2259514,
                    'nutrient': {
                        'id': 1170,
                        'number': '410',
                        'name': 'Pantothenic acid',
                        'rank': 6700,
                        'unitName': 'mg',
                    },
                    'dataPoints': 2,
                    'foodNutrientDerivation': {
                        'code': 'A',
                        'description': 'Analytical',
                        'foodNutrientSource': {
                            'id': 1,
                            'code': '1',
                            'description': 'Analytical or derived from analytical',
                        },
                    },
                    'max': 1.64,
                    'min': 1.53,
                    'median': 1.58,
                    'amount': 1.58,
                },
                {
                    'type': 'FoodNutrient',
                    'id': 2259524,
                    'nutrient': {
                        'id': 1004,
                        'number': '204',
                        'name': 'Total lipid (fat)',
                        'rank': 800,
                        'unitName': 'g',
                    },
                    'dataPoints': 6,
                    'foodNutrientDerivation': {
                        'code': 'A',
                        'description': 'Analytical',
                        'foodNutrientSource': {
                            'id': 1,
                            'code': '1',
                            'description': 'Analytical or derived from analytical',
                        },
                    },
                    'max': 3.99,
                    'min': 2.17,
                    'median': 3.26,
                    'amount': 3.24,
                },
                {
                    'type': 'FoodNutrient',
                    'id': 2259525,
                    'nutrient': {
                        'id': 1005,
                        'number': '205',
                        'name': 'Carbohydrate, by difference',
                        'rank': 1110,
                        'unitName': 'g',
                    },
                    'foodNutrientDerivation': {
                        'code': 'NC',
                        'description': 'Calculated',
                        'foodNutrientSource': {
                            'id': 2,
                            'code': '4',
                            'description': 'Calculated or imputed',
                        },
                    },
                    'amount': 0.000,
                },
                {
                    'type': 'FoodNutrient',
                    'id': 2259526,
                    'nutrient': {
                        'id': 1008,
                        'number': '208',
                        'name': 'Energy',
                        'rank': 300,
                        'unitName': 'kcal',
                    },
                    'foodNutrientDerivation': {
                        'code': 'NC',
                        'description': 'Calculated',
                        'foodNutrientSource': {
                            'id': 2,
                            'code': '4',
                            'description': 'Calculated or imputed',
                        },
                    },
                    'amount': 166,
                },
                {
                    'type': 'FoodNutrient',
                    'id': 2259565,
                    'nutrient': {
                        'id': 1003,
                        'number': '203',
                        'name': 'Protein',
                        'rank': 600,
                        'unitName': 'g',
                    },
                    'foodNutrientDerivation': {
                        'code': 'NC',
                        'description': 'Calculated',
                        'foodNutrientSource': {
                            'id': 2,
                            'code': '4',
                            'description': 'Calculated or imputed',
                        },
                    },
                    'max': 32.9,
                    'min': 31.3,
                    'median': 32.1,
                    'amount': 32.1,
                },
            ],
            'foodAttributes': [],
            'nutrientConversionFactors': [
                {
                    'type': '.CalorieConversionFactor',
                    'proteinValue': 4.27,
                    'fatValue': 9.02,
                    'carbohydrateValue': 3.87,
                },
                {'type': '.ProteinConversionFactor', 'value': 6.25},
            ],
            'isHistoricalReference': False,
            'ndbNumber': 5746,
            'foodPortions': [
                {
                    'id': 121343,
                    'value': 1.0,
                    'measureUnit': {'id': 1043, 'name': 'piece', 'abbreviation': 'piece'},
                    'gramWeight': 174.0,
                    'sequenceNumber': 1,
                    'minYearAcquired': 2012,
                    'amount': 1.0,
                }
            ],
            'publicationDate': '4/1/2019',
            'inputFoods': [
                {
                    'id': 11213,
                    'foodDescription': 'Lorem ipsum',
                    'inputFood': {
                        'foodClass': 'Composite',
                        'description': '......',
                        'publicationDate': '4/1/2019',
                        'foodCategory': {
                            'id': 5,
                            'code': '0500',
                            'description': 'Poultry Products',
                        },
                        'fdcId': 331904,
                        'dataType': 'Sample',
                    },
                },
            ],
            'foodCategory': {'description': 'Poultry Products'},
            'fdcId': 1234567,
            'dataType': 'Foundation',
        }

    def test_regular_response(self):
        """
        Test that the function can read the regular case
        """

        result = extract_info_from_usda(self.usda_data1, 1)
        data = IngredientData(
            name='Foo With Chocolate',
            remote_id='1234567',
            language_id=1,
            energy=166.0,
            protein=32.1,
            carbohydrates=0.0,
            carbohydrates_sugar=None,
            fat=3.24,
            fat_saturated=None,
            fiber=None,
            sodium=None,
            code=None,
            source_name='USDA',
            source_url='https://fdc.nal.usda.gov/',
            common_name='Foo With Chocolate',
            brand='',
            license_id=CC_0_LICENSE_ID,
            license_author='U.S. Department of Agriculture, Agricultural Research Service, '
            'Beltsville Human Nutrition Research Center. FoodData Central.',
            license_title='Foo With Chocolate',
            license_object_url='https://fdc.nal.usda.gov/fdc-app.html#/food-details/1234567/nutrients',
        )

        self.assertEqual(result, data)

    def test_no_energy(self):
        """
        No energy available
        """
        del self.usda_data1['foodNutrients'][3]
        self.assertRaises(KeyError, extract_info_from_usda, self.usda_data1, 1)

    def test_no_nutrients(self):
        """
        No nutrients available
        """
        del self.usda_data1['foodNutrients']
        self.assertRaises(KeyError, extract_info_from_usda, self.usda_data1, 1)

    def test_converting_grams(self):
        """
        Convert from grams (nothing changes)
        """

        entry = {'nutrient': {'unitName': 'g'}, 'amount': '5.0'}
        self.assertEqual(convert_to_grams(entry), 5.0)

    def test_converting_milligrams(self):
        """
        Convert from milligrams
        """

        entry = {'nutrient': {'unitName': 'mg'}, 'amount': '5000'}
        self.assertEqual(convert_to_grams(entry), 5.0)

    def test_converting_unknown_unit(self):
        """
        Convert from unknown unit
        """

        entry = {'nutrient': {'unitName': 'kg'}, 'amount': '5.0'}
        self.assertRaises(ValueError, convert_to_grams, entry)

    def test_converting_invalid_amount(self):
        """
        Convert from invalid amount
        """

        entry = {'nutrient': {'unitName': 'g'}, 'amount': 'invalid'}
        self.assertRaises(ValueError, convert_to_grams, entry)
