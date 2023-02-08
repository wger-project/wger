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
    MagicMock,
    patch,
)

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.models import Ingredient
from wger.nutrition.tasks import (
    fetch_ingredient_image_function,
    logger,
)
from wger.utils.requests import wger_headers

loggerMock = MagicMock()


class MockResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b'2000'

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


class FetchIngredientImageTestCase(WgerTestCase):
    """
    Test fetching an ingredient image
    """

    def test_source(self):
        """
        Test that sources other than OFF are ignored
        """
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.source_name = 'blabla'
        ingredient.save()

        result = fetch_ingredient_image_function(1)
        self.assertEqual(result, None)

    def test_download_off_setting(self):
        """
        Test that no images are fetched if the appropriate setting is not set
        """
        ingredient = Ingredient.objects.get(pk=1)
        ingredient.source_name = 'blabla'
        ingredient.save()

        with self.settings(WGER_SETTINGS={'DOWNLOAD_FROM_OFF': False}):
            result = fetch_ingredient_image_function(1)
            self.assertEqual(result, None)

    @patch('requests.get', return_value=MockResponse())
    @patch.object(logger, 'info')
    def test_download_ingredient(self, mock_logger, mock_request):
        """
        Test that the image is correctly downloaded

        While this way of testing is fragile and depends on what exactly (and when)
        things are logged, it seems to work. Also, directly mocking the logger
        object could probably be done better
        """

        with self.settings(WGER_SETTINGS={'DOWNLOAD_FROM_OFF': True}, TESTING=False):
            result = fetch_ingredient_image_function(1)

            log1 = mock_logger.mock_calls[0]
            log2 = mock_logger.mock_calls[1]
            log3 = mock_logger.mock_calls[2]
            self.assertTrue(log1.called_with('Fetching image for ingredient 1'))
            self.assertTrue(
                log2.called_with(
                    'Trying to fetch image from OFF for Test ingredient 1 (UUID: '
                    'ed608788-811d-4d13-8854-6c42ba545d00)'
                )
            )
            self.assertTrue(log3.called_with('Image successfully saved'))

            request1 = mock_request.mock_calls[0]
            request2 = mock_request.mock_calls[1]
            self.assertTrue(
                request1.called_with(
                    'https://world.openfoodfacts.org/api/v0/product/5055365635003.json',
                    headers=wger_headers()
                )
            )
            self.assertTrue(
                request2.called_with(
                    'https://images.openfoodfacts.org/images/products/00975957/front_en.5.400.jpg',
                    headers=wger_headers()
                )
            )

            self.assertEqual(result, None)
