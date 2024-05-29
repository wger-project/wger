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

# Django
from django.test import SimpleTestCase

# wger
from wger.nutrition.helpers import NutritionalValues


class NutritionalValuesTestCase(SimpleTestCase):
    """
    Tests the Nutritional Values dataclass methods
    """

    def test_kj_property(self):
        """
        Test that the KJ conversion is correct
        """
        values = NutritionalValues(energy=100)
        self.assertAlmostEqual(values.energy_kilojoule, 418.4, places=3)

    def test_addition(self):
        """Test that the addition works correctly"""
        values1 = NutritionalValues(
            energy=100,
            protein=90,
            carbohydrates=80,
            carbohydrates_sugar=70,
            fat=60,
            fat_saturated=50,
            fiber=40,
            sodium=30,
        )
        values2 = NutritionalValues(
            energy=10,
            protein=9,
            carbohydrates=8,
            carbohydrates_sugar=7,
            fat=6,
            fat_saturated=5,
            fiber=4,
            sodium=3,
        )
        values3 = values1 + values2

        self.assertEqual(
            values3,
            NutritionalValues(
                energy=110,
                protein=99,
                carbohydrates=88,
                carbohydrates_sugar=77,
                fat=66,
                fat_saturated=55,
                fiber=44,
                sodium=33,
            ),
        )

    def test_addition_nullable_values(self):
        """Test that the addition works correctly for the nullable values"""

        values1 = NutritionalValues()
        values2 = NutritionalValues(carbohydrates_sugar=10, fat_saturated=20, fiber=30, sodium=40)
        values3 = values1 + values2

        self.assertEqual(
            values3,
            NutritionalValues(
                energy=0,
                protein=0,
                carbohydrates=0,
                carbohydrates_sugar=10,
                fat=0,
                fat_saturated=20,
                fiber=30,
                sodium=40,
            ),
        )
