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
from wger.nutrition.off import (
    IngredientData,
    extract_info_from_off,
)
from wger.utils.constants import ODBL_LICENSE_ID
from wger.utils.models import AbstractSubmissionModel


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
            language_id=1,
            energy=120,
            protein=10,
            carbohydrates=20,
            carbohydrates_sugar=30,
            fat=40,
            fat_saturated=11,
            fibres=None,
            sodium=5,
            code='1234',
            source_name='Open Food Facts',
            source_url='https://world.openfoodfacts.org/api/v2/product/1234.json',
            common_name='Foo with chocolate, 250g package',
            # category='Snack, Cookies, Chocolate',
            brand='The bar company',
            status=AbstractSubmissionModel.STATUS_ACCEPTED,
            license_id=ODBL_LICENSE_ID,
            license_author='open food facts, MrX',
            license_title='Foo with chocolate',
            license_object_url='https://world.openfoodfacts.org/product/1234/',
        )

        # data['category'] = 'Snacks, Chocolate, Cookies'

        self.assertEqual(result, data)

    def test_convert_kj(self):
        """
        Is the category available?
        """
        del self.off_data1['nutriments']['energy-kcal_100g']
        self.off_data1['nutriments']['energy-kj_100g'] = 120

        result = extract_info_from_off(self.off_data1, 1)

        # 120 / KJ_PER_KCAL
        self.assertAlmostEqual(result.energy, 28.6806, 3)

