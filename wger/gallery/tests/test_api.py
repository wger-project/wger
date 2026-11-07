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

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.gallery.models import Image


class GalleryImageApiTestCase(BaseTestCase, ApiBaseTestCase):
    """
    Tests that the gallery API only ever exposes the user's own images

    User test owns image 3, user admin owns images 1 and 2.
    """

    url = '/api/v2/gallery/'

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'{self.url}3/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_contains_only_own_images(self):
        self.authenticate('test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([image['id'] for image in response.json()['results']], [3])

        self.authenticate('admin')
        response = self.client.get(self.url)
        self.assertCountEqual(
            [image['id'] for image in response.json()['results']],
            [1, 2],
        )

    def test_detail_own_image(self):
        self.authenticate('test')
        response = self.client.get(f'{self.url}3/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], 3)

    def test_detail_other_user_image(self):
        self.authenticate('test')
        response = self.client.get(f'{self.url}1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_sets_owner(self):
        self.authenticate('test')

        with open('wger/exercises/tests/protestschwein.jpg', 'rb') as image_file:
            response = self.client.post(
                self.url,
                data={'date': '2024-01-01', 'description': 'test', 'image': image_file},
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        image = Image.objects.get(pk=response.json()['id'])
        self.assertEqual(image.user.username, 'test')

    def test_patch_other_user_image(self):
        self.authenticate('test')
        response = self.client.patch(f'{self.url}1/', data={'description': 'hacked'})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(Image.objects.get(pk=1).description, 'hacked')

    def test_delete_other_user_image(self):
        self.authenticate('test')
        response = self.client.delete(f'{self.url}1/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Image.objects.filter(pk=1).exists())

    def test_delete_own_image(self):
        self.authenticate('test')
        response = self.client.delete(f'{self.url}3/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Image.objects.filter(pk=3).exists())
