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

# wger
from wger.gallery.api.serializers import ImageSerializer
from wger.gallery.models import Image
from wger.utils.powersync import (
    PowerSyncHandler,
    register_handler,
)


@register_handler
class ImageHandler(PowerSyncHandler):
    """
    Creation (and edits that swap the file itself) goes through REST because
    the binary upload can't be carried by the PowerSync push pipeline; only
    metadata-only PATCH and DELETE arrive here. The ``image`` field is dropped
    from the payload because it would otherwise overwrite the ImageField with
    a relative path string.

    The model's ``post_delete`` signal removes the underlying file from
    storage in the same transaction as the row delete.
    """

    model = Image
    serializer_class = ImageSerializer
    supports_create = False

    def preprocess_payload(self, payload):
        payload.pop('image', None)
        return payload
