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

# wger
from wger.weight.api.serializers import WeightEntrySerializer
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)


def handle_update(payload: dict[str, any], user_id: int) -> None:
    """Handle a push event from PowerSync"""
    logger.debug(
        f'Received PowerSync payload for update: {payload}',
    )
    entry = WeightEntry.objects.get(uuid=payload['id'], user_id=user_id)

    if not entry:
        logger.warning(
            f'WeightEntry with UUID {payload["id"]} and user {user_id} not found for update.'
        )
        return

    serializer = WeightEntrySerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated WeightEntry {entry.pk} (uuid={entry.uuid}) for user {user_id}')
    else:
        logger.warning(f'PowerSync update validation failed: {serializer.errors}')


def handle_create(payload: dict[str, any], user_id: int) -> None:
    """Handle a create event from PowerSync"""
    logger.debug(
        f'Received PowerSync payload for create: {payload}',
    )
    serializer = WeightEntrySerializer(data=payload)
    if serializer.is_valid():
        serializer.save(user_id=user_id)
    else:
        logger.warning(f'PowerSync create validation failed: {serializer.errors}')


def handle_delete(payload: dict[str, any], user_id: int) -> None:
    """Handle a delete event from PowerSync"""
    logger.debug(
        f'Received PowerSync payload for delete: {payload}',
    )
    entry = WeightEntry.objects.get(uuid=payload['id'], user_id=user_id)
    if not entry:
        logger.warning(f'WeightEntry with UUID {payload["uuid"]} not found for delete.')
        return
    entry.delete()
