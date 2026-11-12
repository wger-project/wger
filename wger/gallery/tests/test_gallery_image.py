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

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import (
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerTestCase,
)
from wger.gallery.models import Image


class AddGalleryImageTestCase(WgerAddTestCase):
    """
    Tests adding an image to the gallery
    """

    object_class = Image
    url = 'gallery:images:add'
    user_fail = False
    data = {
        'date': datetime.date(2021, 5, 1),
        'user': 1,
        'description': 'Everything going well',
        'image': open('wger/exercises/tests/protestschwein.jpg', 'rb'),
    }


class AddGalleryImageNoDateEXIFTestCase(WgerAddTestCase):
    """
    Tests adding an image to the gallery with no date, should read EXIF data
    """

    object_class = Image
    url = 'gallery:images:add'
    user_fail = False
    data = {
        # No date
        'user': 1,
        'description': 'EXIF Read',
        'image': open('wger/exercises/tests/protestschwein.jpg', 'rb'),
    }

    def post_test_hook(self):
        image = Image.objects.filter(description='EXIF Read').first()
        self.assertEqual(image.date, datetime.date(2026, 3, 1))


class AddGalleryImageNoDateTestCase(WgerAddTestCase):
    """
    Tests adding an image to the gallery with no date, should default to current date
    """

    object_class = Image
    url = 'gallery:images:add'
    user_fail = False
    data = {
        # No date
        'user': 1,
        'description': 'No date provided',
        'image': open('wger/exercises/tests/wildschwein.jpg', 'rb'),
    }

    def post_test_hook(self):
        image = Image.objects.filter(description='No date provided').first()
        self.assertEqual(image.date, datetime.date.today())


class DeleteGalleryImageTestCase(WgerDeleteTestCase):
    """
    Tests deleting a gallery image
    """

    pk = 3
    object_class = Image
    url = 'gallery:images:delete'
    user_success = 'test'
    user_fail = 'admin'


# class EditGalleryImageTestCase(WgerEditTestCase):
#     """
#     Tests editing a gallery image
#     """
#
#     pk = 3
#     object_class = Image
#     url = 'gallery:images:edit'
#     user_success = 'test'
#     user_fail = 'admin'
#     data = {'date': datetime.date(2021, 5, 1),
#             'user': 2,
#             'description': 'Everything going well',
#             'image': open('wger/exercises/tests/protestschwein.jpg', 'rb')}


class EditGalleryImageOwnerTestCase(WgerTestCase):
    """
    Editing an image keeps its owner, whatever user is submitted
    """

    def setUp(self):
        super().setUp()
        self.owner = User.objects.get(username='test')
        self.other = User.objects.get(username='admin')
        self.image = Image.objects.filter(user=self.owner).first()
        with open('wger/exercises/tests/wildschwein.jpg', 'rb') as image_file:
            self.image.image.storage.save(self.image.image.name, File(image_file))
        self.user_login('test')

    def test_submitted_user_is_ignored(self):
        response = self.client.post(
            reverse('gallery:images:edit', kwargs={'pk': self.image.pk}),
            {'date': '2021-05-01', 'user': self.other.pk, 'description': 'moved'},
        )

        self.assertEqual(response.status_code, 302)
        self.image.refresh_from_db()
        self.assertEqual(self.image.description, 'moved')
        self.assertEqual(self.image.user, self.owner)

    def test_submitted_user_is_ignored_with_new_file(self):
        with open('wger/exercises/tests/protestschwein.jpg', 'rb') as image_file:
            response = self.client.post(
                reverse('gallery:images:edit', kwargs={'pk': self.image.pk}),
                {'date': '2021-05-01', 'user': self.other.pk, 'image': image_file},
            )

        self.assertEqual(response.status_code, 302)
        self.image.refresh_from_db()
        self.assertEqual(self.image.user, self.owner)
        self.assertTrue(self.image.image.name.startswith(f'gallery/{self.owner.pk}/'))


class AddGalleryImageAnonymousTestCase(WgerTestCase):
    """
    Anonymous visitors are sent to the login page instead of the upload form
    """

    def test_get(self):
        response = self.client.get(reverse('gallery:images:add'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(f'{settings.LOGIN_URL}?next='))

    def test_post(self):
        count_before = Image.objects.count()

        with open('wger/exercises/tests/protestschwein.jpg', 'rb') as image:
            response = self.client.post(
                reverse('gallery:images:add'),
                {'date': datetime.date(2021, 5, 1), 'user': 1, 'image': image},
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Image.objects.count(), count_before)
