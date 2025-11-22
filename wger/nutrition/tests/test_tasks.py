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
import datetime
from unittest.mock import (
    ANY,
    MagicMock,
    patch,
)

# Django
from django.utils import timezone

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


mock_off_response = {
    'image_front_url': 'https://images.openfoodfacts.org/images/products/00975957/front_en.5.400.jpg',
    'images': {
        'front_en': {
            'imgid': '12345',
        },
        '12345': {'uploader': 'Mr Foobar'},
    },
}

mock_off_response_no_front_url = {
    'images': {
        'front_en': {
            'imgid': '12345',
        },
        '12345': {'uploader': 'Mr Foobar'},
    },
}


class MockOffImageResponse:
    image_bytes = [0, 1, 2, 3]
    response = type('obj', (object,), {'content': b'mock_content'})()


class MockWgerApiResponse:
    def __init__(self):
        self.status_code = 200
        self.content = b'2000'

    @staticmethod
    def json():
        return {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': 1,
                    'uuid': '188324b5-587f-42d7-9abc-d2ca64c73d45',
                    'ingredient_id': '12345',
                    'ingredient_uuid': 'e9baa8bd-84fc-4756-8d90-5b9739b06cf8',
                    'image': 'http://localhost:8000/media/ingredients/1/188324b5-587f-42d7-9abc-d2ca64c73d45.jpg',
                    'created': '2023-03-15T23:20:10.969369+01:00',
                    'last_update': '2023-03-15T23:20:10.969369+01:00',
                    'size': 20179,
                    'width': 400,
                    'height': 166,
                    'license': 1,
                    'license_author': 'Tester McTest',
                    'license_author_url': 'https://example.com/editors/mcLovin',
                    'license_title': '',
                    'license_object_url': '',
                    'license_derivative_source_url': '',
                }
            ],
        }


class FetchIngredientImageTestCase(WgerTestCase):
    """
    Test fetching an ingredient image
    """

    @patch(
        'openfoodfacts.api.ProductResource.get',
        autospec=True,
    )
    @patch.object(
        logger,
        'info',
        autospec=True,
    )
    def test_source(self, mock_logger: MagicMock, mock_request: MagicMock):
        """
        Test that sources other than OFF are ignored
        """
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.source_name = 'blabla'
        ingredient.save()

        with self.settings(WGER_SETTINGS={'DOWNLOAD_INGREDIENTS_FROM': 'FOO'}):
            result = fetch_ingredient_image(1)
            mock_logger.assert_not_called()
            mock_request.assert_not_called()
            self.assertIsNone(result)

    @patch('openfoodfacts.api.ProductResource.get', autospec=True)
    @patch.object(logger, 'info', autospec=True)
    def test_download_off_setting(self, mock_logger: MagicMock, mock_request: MagicMock):
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

    @patch('openfoodfacts.api.ProductResource.get', autospec=True)
    @patch('wger.nutrition.models.Image.from_json', autospec=True)
    @patch.object(logger, 'info', autospec=True)
    def test_last_new_image_date(
        self,
        mock_logger: MagicMock,
        mock_from_json: MagicMock,
        mock_request: MagicMock,
    ):
        """
        Test that no images are fetched if we already checked recently
        """
        last_checked = timezone.now() - datetime.timedelta(days=1)

        ingredient = Ingredient.objects.get(pk=1)
        ingredient.last_image_check = last_checked
        ingredient.save()

        with self.settings(
            TESTING=False,
            WGER_SETTINGS={
                'DOWNLOAD_INGREDIENTS_FROM': DOWNLOAD_INGREDIENT_OFF,
                'INGREDIENT_IMAGE_CHECK_INTERVAL': datetime.timedelta(days=5),
            },
        ):
            # Act
            result = fetch_ingredient_image(1)
            ingredient.refresh_from_db()

            # Assert
            mock_from_json.assert_not_called()
            mock_logger.assert_not_called()
            mock_request.assert_not_called()
            self.assertIsNone(result)
            self.assertEqual(ingredient.last_image_check, last_checked)

    @patch('wger.nutrition.sync.download_image', return_value=MockOffImageResponse, autospec=True)
    @patch('openfoodfacts.api.ProductResource.get', return_value=mock_off_response, autospec=True)
    @patch('wger.nutrition.models.Image.from_json', autospec=True)
    @patch.object(logger, 'info', autospec=True)
    def test_old_last_image_check_date(
        self,
        mock_logger: MagicMock,
        mock_from_json: MagicMock,
        mock_request: MagicMock,
        mock_download_image: MagicMock,
    ):
        """
        Test that images are fetched if we checked a long time ago
        """
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.last_image_check = timezone.now() - datetime.timedelta(days=200)
        ingredient.save()

        with self.settings(
            TESTING=False,
            WGER_SETTINGS={
                'DOWNLOAD_INGREDIENTS_FROM': DOWNLOAD_INGREDIENT_OFF,
                'INGREDIENT_IMAGE_CHECK_INTERVAL': datetime.timedelta(days=5),
            },
        ):
            # Act
            result = fetch_ingredient_image(1)
            ingredient.refresh_from_db()

            # Assert
            mock_from_json.assert_called()
            mock_download_image.assert_called_with(
                'https://images.openfoodfacts.org/images/products/00975957/front_en.5.400.jpg',
                return_struct=True,
            )
            mock_logger.assert_any_call('Fetching image for ingredient 1')
            mock_request.assert_called_with(
                ANY,
                '1234567890987654321',
                fields=['images', 'image_front_url'],
            )

            self.assertIsNone(result)
            self.assertAlmostEqual(
                ingredient.last_image_check, timezone.now(), delta=datetime.timedelta(seconds=1)
            )

    @patch('wger.nutrition.sync.download_image', autospec=True, return_value=MockOffImageResponse)
    @patch(
        'openfoodfacts.api.ProductResource.get',
        autospec=True,
        return_value=mock_off_response_no_front_url,
    )
    @patch('wger.nutrition.models.Image.from_json', autospec=True)
    @patch.object(logger, 'info', autospec=True)
    def test_update_handle_no_front_url_key(
        self,
        mock_logger: MagicMock,
        mock_from_json: MagicMock,
        mock_request: MagicMock,
        mock_download_image: MagicMock,
    ):
        """
        Properly handles case where OFF response does not contain the 'image_front_url' key
        """
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.last_image_check = None
        ingredient.save()

        with self.settings(
            TESTING=False,
            WGER_SETTINGS={'DOWNLOAD_INGREDIENTS_FROM': DOWNLOAD_INGREDIENT_OFF},
        ):
            # Act
            result = fetch_ingredient_image(1)
            ingredient.refresh_from_db()

            # Assert
            mock_logger.assert_called()
            mock_from_json.assert_not_called()
            mock_download_image.assert_not_called()
            mock_request.assert_called()

            self.assertIsNone(result)
            self.assertAlmostEqual(
                ingredient.last_image_check, timezone.now(), delta=datetime.timedelta(seconds=1)
            )

    @patch('wger.nutrition.sync.download_image', return_value=MockOffImageResponse, autospec=True)
    @patch('openfoodfacts.api.ProductResource.get', return_value=mock_off_response, autospec=True)
    @patch('wger.nutrition.models.Image.from_json', autospec=True)
    @patch.object(logger, 'info', autospec=True)
    def test_download_ingredient_off(
        self,
        mock_logger: MagicMock,
        mock_from_json: MagicMock,
        mock_request: MagicMock,
        mock_download_image: MagicMock,
    ):
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
            # Act
            result = fetch_ingredient_image(1)

            # Assert
            # print(mock_request.mock_calls)
            mock_request.assert_called_with(
                ANY,
                '1234567890987654321',
                fields=['images', 'image_front_url'],
            )
            mock_download_image.assert_called_with(
                'https://images.openfoodfacts.org/images/products/00975957/front_en.5.400.jpg',
                return_struct=True,
            )
            mock_logger.assert_any_call('Fetching image for ingredient 1')
            mock_logger.assert_any_call(
                'Trying to fetch image from OFF for "Test ingredient 1" '
                '(7908c204-907f-4b1e-ad4e-f482e9769ade)'
            )
            mock_logger.assert_any_call('Image successfully saved')
            mock_from_json.assert_called()

            self.assertIsNone(result)

    @patch('requests.get', return_value=MockWgerApiResponse(), autospec=True)
    @patch('wger.nutrition.models.Image.from_json', autospec=True)
    @patch.object(logger, 'info', autospec=True)
    def test_download_ingredient_wger(
        self,
        mock_logger: MagicMock,
        mock_from_json: MagicMock,
        mock_request: MagicMock,
    ):
        """
        Test that the image is correctly downloaded

        While this way of testing is fragile and depends on what exactly (and when)
        things are logged, it seems to work. Also, directly mocking the logger
        object could probably be done better
        """

        with self.settings(
            WGER_SETTINGS={'DOWNLOAD_INGREDIENTS_FROM': DOWNLOAD_INGREDIENT_WGER}, TESTING=False
        ):
            # Act
            result = fetch_ingredient_image(1)

            # Assert
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
            self.assertIsNone(result)
