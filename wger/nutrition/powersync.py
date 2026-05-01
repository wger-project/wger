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
from wger.nutrition.api.serializers import (
    LogItemSerializer,
    NutritionPlanSerializer,
)
from wger.nutrition.api.views import (
    LogItemViewSet,
    NutritionPlanViewSet,
)
from wger.nutrition.models import (
    LogItem,
    NutritionPlan,
)
from wger.utils.viewsets import check_fk_ownership


logger = logging.getLogger(__name__)


def handle_update_plan(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PATCH event for a nutritional plan.

    Creation still goes through REST (the backend assigns the integer PK and
    `creation_date`), so there is no `handle_create_plan` here — only edit
    and delete are part of the PowerSync upload pipeline.
    """
    logger.debug(f'Received PowerSync payload for nutritional plan update: {payload}')
    try:
        entry = NutritionPlan.objects.get(pk=payload['id'], user_id=user_id)
    except NutritionPlan.DoesNotExist:
        logger.warning(
            f'NutritionPlan with id {payload["id"]} and user {user_id} not found for update.'
        )
        return {
            'error': 'Not found',
            'details': f'NutritionPlan with id {payload["id"]} not found',
        }

    if not check_fk_ownership(payload, NutritionPlanViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'NutritionPlan references an object you do not own'}

    serializer = NutritionPlanSerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated NutritionPlan {entry.pk} for user {user_id}')
        return None
    logger.warning(f'PowerSync nutritional plan update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_plan(payload: dict[str, Any], user_id: int) -> dict | None:
    """
    Handle a PowerSync DELETE event for a nutritional plan.

    Django's FK CASCADE removes all dependent meals, meal items and diary
    log entries in the same transaction.
    """
    logger.debug(f'Received PowerSync payload for nutritional plan delete: {payload}')
    try:
        entry = NutritionPlan.objects.get(pk=payload['id'], user_id=user_id)
    except NutritionPlan.DoesNotExist:
        logger.warning(f'NutritionPlan with id {payload["id"]} not found for delete.')
        return {
            'error': 'Not found',
            'details': f'NutritionPlan with id {payload["id"]} not found',
        }
    entry.delete()
    logger.info(f'Deleted NutritionPlan {payload["id"]} for user {user_id}')
    return None

#
# Log items (nutrition diary)
#

def handle_create_log(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PUT event for a diary log entry."""
    logger.debug(f'Received PowerSync payload for log create: {payload}')

    if not check_fk_ownership(payload, LogItemViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'LogItem references an object you do not own'}

    serializer = LogItemSerializer(data=payload)
    if serializer.is_valid():
        serializer.save(uuid=payload['id'])
        logger.info(f'Created LogItem (uuid={payload["id"]}) for user {user_id}')
        return None
    logger.warning(f'PowerSync log create validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_update_log(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PATCH event for a diary log entry."""
    logger.debug(f'Received PowerSync payload for log update: {payload}')
    try:
        entry = LogItem.objects.get(uuid=payload['id'], plan__user_id=user_id)
    except LogItem.DoesNotExist:
        logger.warning(
            f'LogItem with uuid {payload["id"]} and user {user_id} not found for update.'
        )
        return {'error': 'Not found', 'details': f'LogItem with uuid {payload["id"]} not found'}

    if not check_fk_ownership(payload, LogItemViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'LogItem references an object you do not own'}

    # Drop 'id' from the patch, the row is already resolved by uuid above
    payload.pop('id', None)
    serializer = LogItemSerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated LogItem {entry.pk} (uuid={entry.uuid}) for user {user_id}')
        return None
    logger.warning(f'PowerSync log update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_log(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync DELETE event for a diary log entry."""
    logger.debug(f'Received PowerSync payload for log delete: {payload}')
    try:
        entry = LogItem.objects.get(uuid=payload['id'], plan__user_id=user_id)
    except LogItem.DoesNotExist:
        logger.warning(f'LogItem with uuid {payload["id"]} not found for delete.')
        return {'error': 'Not found', 'details': f'LogItem with uuid {payload["id"]} not found'}
    entry.delete()
    logger.info(f'Deleted LogItem (uuid={payload["id"]}) for user {user_id}')
    return None
