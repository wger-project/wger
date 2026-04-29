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
from wger.nutrition.api.serializers import NutritionPlanSerializer
from wger.nutrition.api.views import NutritionPlanViewSet
from wger.nutrition.models import NutritionPlan
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
