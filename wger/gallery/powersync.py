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
import logging
from typing import Any

# wger
from wger.gallery.api.serializers import ImageSerializer
from wger.gallery.models import Image


logger = logging.getLogger(__name__)


def handle_update_image(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PATCH event for a gallery image.

    Creation still goes through REST (the file upload itself can't be carried
    by the PowerSync push pipeline), so there is no `handle_create_image`. Edits
    that swap the image file likewise go through REST, only metadata-only edits
    (date, description) reach this handler.
    """
    logger.debug(f'Received PowerSync payload for gallery image update: {payload}')
    try:
        entry = Image.objects.get(pk=payload['id'], user_id=user_id)
    except Image.DoesNotExist:
        logger.warning(
            f'Gallery image with id {payload["id"]} and user {user_id} not found for update.'
        )
        return {
            'error': 'Not found',
            'details': f'Gallery image with id {payload["id"]} not found',
        }

    # Drop the binary `image` field — the file is owned by Django and only
    # changes via REST. PowerSync only carries the relative path, which would
    # break the ImageField on a partial update.
    payload.pop('image', None)

    serializer = ImageSerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated gallery image {entry.pk} for user {user_id}')
        return None
    logger.warning(f'PowerSync gallery image update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_image(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync DELETE event for a gallery image.

    The model's `post_delete` signal also removes the underlying file from
    storage in the same transaction.
    """
    logger.debug(f'Received PowerSync payload for gallery image delete: {payload}')
    try:
        entry = Image.objects.get(pk=payload['id'], user_id=user_id)
    except Image.DoesNotExist:
        logger.warning(f'Gallery image with id {payload["id"]} not found for delete.')
        return {
            'error': 'Not found',
            'details': f'Gallery image with id {payload["id"]} not found',
        }
    entry.delete()
    logger.info(f'Deleted gallery image {payload["id"]} for user {user_id}')
    return None
