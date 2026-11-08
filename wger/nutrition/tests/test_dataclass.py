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
from dataclasses import replace
from decimal import Decimal

# Django
from django.test import SimpleTestCase

# wger
from wger.nutrition.dataclasses import IngredientData
from wger.utils.constants import CC_0_LICENSE_ID


NUTRIENT_FIELDS = (
    'energy',
    'protein',
    'carbohydrates',
    'carbohydrates_sugar',
    'fat',
    'fat_saturated',
    'fiber',
    'sodium',
)


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
        """Test that the validation proceeds with correct data"""
        self.assertEqual(self.ingredient_data.sanity_checks(), None)

    def test_validation_negative_nutrients(self):
        """Reject negatives even when the energy plausibility check is skipped."""
        baseline = replace(self.ingredient_data, **dict.fromkeys(NUTRIENT_FIELDS, 0))
        for field in NUTRIENT_FIELDS:
            for value in (-1, -1.0, Decimal('-1')):
                with self.subTest(field=field, value=value, number_type=type(value)):
                    ingredient = replace(baseline, **{field: value})
                    with self.assertRaisesRegex(ValueError, field):
                        ingredient.sanity_checks()

    def test_validation_non_finite_nutrients(self):
        """Reject NaN and infinities before comparisons or energy calculations."""
        values = (
            float('nan'),
            float('inf'),
            float('-inf'),
            Decimal('NaN'),
            Decimal('sNaN'),
            Decimal('Infinity'),
            Decimal('-Infinity'),
        )
        baseline = replace(self.ingredient_data, **dict.fromkeys(NUTRIENT_FIELDS, 0))
        for field in NUTRIENT_FIELDS:
            for value in values:
                with self.subTest(field=field, value=value, number_type=type(value)):
                    ingredient = replace(baseline, **{field: value})
                    with self.assertRaisesRegex(ValueError, field):
                        ingredient.sanity_checks()

    def test_validation_zero_nutrients(self):
        """Zero remains valid for every supported numeric type."""
        for number_type in (int, float, Decimal):
            with self.subTest(number_type=number_type):
                ingredient = replace(
                    self.ingredient_data,
                    **dict.fromkeys(NUTRIENT_FIELDS, number_type(0)),
                )
                self.assertIsNone(ingredient.sanity_checks())

    def test_validation_bigger_100(self):
        """
        Test the validation for values bigger than 100
        """
        self.ingredient_data.protein = 101
        self.assertRaises(ValueError, self.ingredient_data.sanity_checks)

    def test_validation_macro_sum_within_tolerance(self):
        """
        Test that a macro sum slightly over 100 is accepted (label tolerances)
        """
        self.ingredient_data.protein = 12
        self.ingredient_data.carbohydrates = 45
        self.ingredient_data.fat = 47
        self.ingredient_data.energy = 604
        self.assertEqual(self.ingredient_data.sanity_checks(), None)

    def test_validation_macro_sum_over_tolerance(self):
        """
        Test that a macro sum over 105 is rejected
        """
        self.ingredient_data.protein = 15
        self.ingredient_data.carbohydrates = 45
        self.ingredient_data.fat = 47
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

    def test_validation_energy_mismatch(self):
        """
        Test that a declared energy far off the computed one is rejected
        """
        self.ingredient_data.energy = 700
        self.assertRaises(ValueError, self.ingredient_data.sanity_checks)

    def test_validation_energy_within_tolerance(self):
        """
        Test that a declared energy within the tolerance is accepted
        """
        # Computed energy is 32.1*4 + 3.24*9 = 157.56 kcal
        self.ingredient_data.energy = 200
        self.assertEqual(self.ingredient_data.sanity_checks(), None)

    def test_validation_energy_fiber_counts(self):
        """
        Test that fiber contributes 2 kcal/g to the computed energy
        """
        self.ingredient_data.protein = 0
        self.ingredient_data.carbohydrates = 0
        self.ingredient_data.fat = 0
        self.ingredient_data.fiber = 50
        self.ingredient_data.energy = 100
        self.assertEqual(self.ingredient_data.sanity_checks(), None)

    def test_validation_energy_low_values_skipped(self):
        """
        Test that very low energy values are not checked at all
        """
        self.ingredient_data.protein = 0
        self.ingredient_data.carbohydrates = 0
        self.ingredient_data.fat = 0
        self.ingredient_data.energy = 13
        self.assertEqual(self.ingredient_data.sanity_checks(), None)

    def test_validation_nutriscore_valid(self):
        """
        Test that valid nutriscore values are accepted
        """
        for score in ('a', 'b', 'c', 'd', 'e', None):
            self.ingredient_data.nutriscore = score
            self.assertEqual(self.ingredient_data.sanity_checks(), None)

    def test_validation_nutriscore_invalid(self):
        """
        Test that invalid nutriscore values are rejected
        """
        self.ingredient_data.nutriscore = 'z'
        self.assertRaises(ValueError, self.ingredient_data.sanity_checks)
