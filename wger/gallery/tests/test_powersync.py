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

# wger
from wger.core.tests import powersync_base_test
from wger.gallery.models import Image


# Pinned in test-gallery-images.json
IMAGE_OWNED = 3  # user 'test'


class GalleryImagePowerSyncTestCase(
    powersync_base_test.PowerSyncBaseTestCase,
    powersync_base_test.PowerSyncCreateNotAllowedTestCase,
    powersync_base_test.PowerSyncUpdateTestCase,
    powersync_base_test.PowerSyncDeleteTestCase,
):
    """
    PowerSync handlers for gallery.Image. Creation (and edits that swap the
    binary file) go through REST because PowerSync can't carry the upload,
    only metadata edits and deletes reach us via PowerSync.
    """

    table = 'gallery_image'
    resource = Image

    pk_owned = IMAGE_OWNED

    update_payload = {
        'id': pk_owned,
        'description': 'Renamed via PowerSync',
    }

    create_payload = {'id': 9999, 'description': 'should not be created'}
