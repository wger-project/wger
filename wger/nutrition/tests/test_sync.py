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

# Standard Library
from decimal import Decimal
from unittest.mock import patch
from uuid import UUID

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.models import Ingredient
from wger.nutrition.sync import sync_ingredients
from wger.utils.requests import wger_headers


class MockIngredientResponse:
    def __init__(self):
        self.status_code = 200
        self.content = b'1234'

    # yapf: disable
    @staticmethod
    def json():
        return {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "uuid": "7908c204-907f-4b1e-ad4e-f482e9769ade",
                    "code": "0013087245950",
                    "name": "Gâteau double chocolat",
                    "created": "2020-12-20T01:00:00+01:00",
                    "last_update": "2020-12-20T01:00:00+01:00",
                    "energy": 360,
                    "protein": "5.000",
                    "carbohydrates": "45.000",
                    "carbohydrates_sugar": "27.000",
                    "fat": "18.000",
                    "fat_saturated": "4.500",
                    "fiber": "2.000",
                    "sodium": "0.356",
                    "license": 5,
                    "license_title": " Gâteau double chocolat ",
                    "license_object_url": "",
                    "license_author": "Open Food Facts",
                    "license_author_url": "",
                    "license_derivative_source_url": "",
                    "language": 2
                },
                {
                    "id": 22634,
                    "uuid": "582f1b7f-a8bd-4951-9edd-247bc68b28f4",
                    "code": "3181238941963",
                    "name": "Maxi Hot Dog New York Style",
                    "created": "2020-12-20T01:00:00+01:00",
                    "last_update": "2020-12-20T01:00:00+01:00",
                    "energy": 256,
                    "protein": "11.000",
                    "carbohydrates": "27.000",
                    "carbohydrates_sugar": "5.600",
                    "fat": "11.000",
                    "fat_saturated": "4.600",
                    "fiber": None,
                    "sodium": "0.820",
                    "license": 5,
                    "license_title": " Maxi Hot Dog New York Style",
                    "license_object_url": "",
                    "license_author": "Open Food Facts",
                    "license_author_url": "",
                    "license_derivative_source_url": "",
                    "language": 3
                },
            ]
        }
    # yapf: enable


class TestSyncMethods(WgerTestCase):
    @patch('requests.get', return_value=MockIngredientResponse())
    def test_ingredient_sync(self, mock_request):
        # Arrange
        ingredient = Ingredient.objects.get(pk=1)

        self.assertEqual(Ingredient.objects.count(), 14)
        self.assertEqual(ingredient.name, 'Test ingredient 1')
        self.assertEqual(ingredient.energy, 176)
        self.assertAlmostEqual(ingredient.protein, Decimal(25.63), 2)
        self.assertEqual(ingredient.code, '1234567890987654321')

        # Act
        sync_ingredients(lambda x: x)
        mock_request.assert_called_with(
            'https://wger.de/api/v2/ingredient/?limit=999',
            headers=wger_headers(),
        )

        # Assert
        self.assertEqual(Ingredient.objects.count(), 15)

        ingredient = Ingredient.objects.get(pk=1)
        self.assertEqual(ingredient.name, 'Gâteau double chocolat')
        self.assertEqual(ingredient.energy, 360)
        self.assertAlmostEqual(ingredient.protein, Decimal(5), 2)
        self.assertEqual(ingredient.code, '0013087245950')
        self.assertEqual(ingredient.license.pk, 5)
        self.assertEqual(ingredient.uuid, UUID('7908c204-907f-4b1e-ad4e-f482e9769ade'))

        new_ingredient = Ingredient.objects.get(uuid='582f1b7f-a8bd-4951-9edd-247bc68b28f4')
        self.assertEqual(new_ingredient.name, 'Maxi Hot Dog New York Style')
        self.assertEqual(new_ingredient.energy, 256)
        self.assertAlmostEqual(new_ingredient.protein, Decimal(11), 2)
        self.assertEqual(new_ingredient.code, '3181238941963')
