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

# wger
from wger.core.tests.base_testcase import (
    WgerAddTestCase,
    WgerDeleteTestCase,
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
