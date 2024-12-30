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

# Standard Library
from unittest.mock import (
    ANY,
    patch,
)

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.models import Ingredient
from wger.nutrition.sync import (
    fetch_ingredient_image,
    logger,
)
from wger.utils.constants import (
    DOWNLOAD_INGREDIENT_OFF,
    DOWNLOAD_INGREDIENT_WGER,
)
from wger.utils.requests import wger_headers


class MockOffResponse:
    def __init__(self):
        self.status_code = 200
        self.ok = True
        self.content = b'2000'

    # yapf: disable
    @staticmethod
    def json():
        return {
            "product": {
                'image_front_url':
                    'https://images.openfoodfacts.org/images/products/00975957/front_en.5.400.jpg',
                'images': {
                    'front_en': {
                        'imgid': '12345',
                    },
                    '12345': {
                        'uploader': 'Mr Foobar'
                    }
                }
            },
        }
    # yapf: disable


class MockWgerApiResponse:
    def __init__(self):
        self.status_code = 200
        self.content = b'2000'

    # yapf: disable
    @staticmethod
    def json():
        return {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "uuid": "188324b5-587f-42d7-9abc-d2ca64c73d45",
                    "ingredient_id": "12345",
                    "ingredient_uuid": "e9baa8bd-84fc-4756-8d90-5b9739b06cf8",
                    "image": "http://localhost:8000/media/ingredients/1/188324b5-587f-42d7-9abc-d2ca64c73d45.jpg",
                    "created": "2023-03-15T23:20:10.969369+01:00",
                    "last_update": "2023-03-15T23:20:10.969369+01:00",
                    "size": 20179,
                    "width": 400,
                    "height": 166,
                    "license": 1,
                    "license_author": "Tester McTest",
                    "license_author_url": "https://example.com/editors/mcLovin",
                    "license_title": "",
                    "license_object_url": "",
                    "license_derivative_source_url": ""
                }
            ]
        }
    # yapf: enable


class FetchIngredientImageTestCase(WgerTestCase):
    """
    Test fetching an ingredient image
    """

    @patch('requests.get')
    @patch.object(logger, 'info')
    def test_source(self, mock_logger, mock_request):
        """
        Test that sources other than OFF are ignored
        """
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.source_name = 'blabla'
        ingredient.save()

        with self.settings(WGER_SETTINGS={'DOWNLOAD_INGREDIENTS_FROM': True}):
            result = fetch_ingredient_image(1)
            mock_logger.assert_not_called()
            mock_request.assert_not_called()
            self.assertEqual(result, None)

    @patch('requests.get')
    @patch.object(logger, 'info')
    def test_download_off_setting(self, mock_logger, mock_request):
        """
        Test that no images are fetched if the appropriate setting is not set
        """
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.source_name = 'blabla'
        ingredient.save()

        with self.settings(WGER_SETTINGS={'DOWNLOAD_INGREDIENTS_FROM': False}):
            result = fetch_ingredient_image(1)
            mock_logger.assert_not_called()
            mock_request.assert_not_called()
            self.assertEqual(result, None)

    @patch('requests.get', return_value=MockOffResponse())
    @patch('wger.nutrition.models.Image.from_json')
    @patch.object(logger, 'info')
    def test_download_ingredient_off(self, mock_logger, mock_from_json, mock_request):
        """
        Test that the image is correctly downloaded

        While this way of testing is fragile and depends on what exactly (and when)
        things are logged, it seems to work. Also, directly mocking the logger
        object could probably be done better
        """

        with self.settings(
            WGER_SETTINGS={'DOWNLOAD_INGREDIENTS_FROM': DOWNLOAD_INGREDIENT_OFF},
            TESTING=False,
        ):
            result = fetch_ingredient_image(1)

            mock_logger.assert_any_call('Fetching image for ingredient 1')
            mock_logger.assert_any_call(
                'Trying to fetch image from OFF for Test ingredient 1 (UUID: '
                '7908c204-907f-4b1e-ad4e-f482e9769ade)'
            )
            mock_logger.assert_any_call('Image successfully saved')

            # print(mock_request.mock_calls)
            mock_request.assert_any_call(
                'https://world.openfoodfacts.org/api/v2/product/5055365635003.json?fields=images,image_front_url',
                headers=wger_headers(),
                timeout=ANY,
            )
            mock_request.assert_any_call(
                'https://openfoodfacts-images.s3.eu-west-3.amazonaws.com/data/123/456/789/0987654321/12345.jpg',
                headers=wger_headers(),
            )
            mock_from_json.assert_called()

            self.assertEqual(result, None)

    @patch('requests.get', return_value=MockWgerApiResponse())
    @patch('wger.nutrition.models.Image.from_json')
    @patch.object(logger, 'info')
    def test_download_ingredient_wger(self, mock_logger, mock_from_json, mock_request):
        """
        Test that the image is correctly downloaded

        While this way of testing is fragile and depends on what exactly (and when)
        things are logged, it seems to work. Also, directly mocking the logger
        object could probably be done better
        """

        with self.settings(
            WGER_SETTINGS={'DOWNLOAD_INGREDIENTS_FROM': DOWNLOAD_INGREDIENT_WGER}, TESTING=False
        ):
            result = fetch_ingredient_image(1)

            mock_logger.assert_any_call('Fetching image for ingredient 1')
            mock_logger.assert_any_call(
                'Trying to fetch image from WGER for Test ingredient 1 (UUID: '
                '7908c204-907f-4b1e-ad4e-f482e9769ade)'
            )

            mock_request.assert_any_call(
                'https://wger.de/api/v2/ingredient-image/?ingredient__uuid=7908c204-907f-4b1e-ad4e-f482e9769ade',
                headers=wger_headers(),
            )
            mock_request.assert_any_call(
                'http://localhost:8000/media/ingredients/1/188324b5-587f-42d7-9abc-d2ca64c73d45.jpg',
                headers=wger_headers(),
            )
            mock_from_json.assert_called()

            self.assertEqual(result, None)
