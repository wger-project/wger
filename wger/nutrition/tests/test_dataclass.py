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
from wger.utils.constants import CC_0_LICENSE_ID


class IngredientDataclassTestCase(SimpleTestCase):
    """
    Test validation rules
    """

    ingredient_data: IngredientData

    def setUp(self):
        self.ingredient_data = IngredientData(
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
            source_url='',
            common_name='',
            brand='',
            license_id=CC_0_LICENSE_ID,
            license_author='',
            license_title='',
            license_object_url='',
        )

    def test_validation_ok(self):
        """"""
        self.assertEqual(self.ingredient_data.sanity_checks(), None)

    def test_validation_bigger_100(self):
        """
        Test the validation for values bigger than 100
        """
        self.ingredient_data.protein = 101
        self.assertRaises(ValueError, self.ingredient_data.sanity_checks)

    def test_validation_saturated_fat(self):
        """
        Test the validation for saturated fat
        """
        self.ingredient_data.fat = 20
        self.ingredient_data.fat_saturated = 30
        self.assertRaises(ValueError, self.ingredient_data.sanity_checks)

    def test_validation_sugar(self):
        """
        Test the validation for sugar
        """
        self.ingredient_data.carbohydrates = 20
        self.ingredient_data.carbohydrates_sugar = 30
        self.assertRaises(ValueError, self.ingredient_data.sanity_checks)

    def test_validation_energy_fat(self):
        """
        Test the validation for energy and fat
        """
        self.ingredient_data.energy = 200
        self.ingredient_data.fat = 30  # generates 30 * 9 = 270 kcal
        self.assertRaisesRegex(
            ValueError,
            'Energy calculated from fat',
            self.ingredient_data.sanity_checks,
        )

    def test_validation_energy_protein(self):
        """
        Test the validation for energy and protein
        """
        self.ingredient_data.energy = 100
        self.ingredient_data.protein = 30  # generates 30 * 4 = 120 kcal
        self.assertRaisesRegex(
            ValueError,
            'Energy calculated from protein',
            self.ingredient_data.sanity_checks,
        )

    def test_validation_energy_carbohydrates(self):
        """
        Test the validation for energy and carbohydrates
        """
        self.ingredient_data.energy = 100
        self.ingredient_data.carbohydrates = 30  # generates 30 * 4 = 120 kcal
        self.assertRaisesRegex(
            ValueError,
            'Energy calculated from carbohydrates',
            self.ingredient_data.sanity_checks,
        )

    def test_validation_energy_total(self):
        """
        Test the validation for energy total
        """
        self.ingredient_data.energy = 200  # less than 120 + 80 + 90
        self.ingredient_data.protein = 30  # generates 30 * 4 = 120 kcal
        self.ingredient_data.carbohydrates = 20  # generates 20 * 4 = 80 kcal
        self.ingredient_data.fat = 10  # generates 10 * 9 = 90 kcal
        self.assertRaisesRegex(
            ValueError,
            'Total energy calculated',
            self.ingredient_data.sanity_checks,
        )
