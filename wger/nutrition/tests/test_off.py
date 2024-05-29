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
from wger.nutrition.off import extract_info_from_off
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
