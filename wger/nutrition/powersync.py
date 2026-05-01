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
    MealItemSerializer,
    MealSerializer,
    NutritionPlanSerializer,
)
from wger.nutrition.api.views import (
    LogItemViewSet,
    MealItemViewSet,
    MealViewSet,
    NutritionPlanViewSet,
)
from wger.nutrition.models import (
    LogItem,
    Meal,
    MealItem,
    NutritionPlan,
)
from wger.utils.powersync import resolve_uuid_fk
from wger.utils.viewsets import check_fk_ownership


logger = logging.getLogger(__name__)


#
# Nutritional plans
#


def handle_create_plan(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PUT event for a nutritional plan.

    The client generates the row's UUID; the backend honours it via
    `serializer.save(uuid=...)`. The owning user is forced to the
    authenticated one regardless of payload contents.
    """
    logger.debug(f'Received PowerSync payload for nutritional plan create: {payload}')

    serializer = NutritionPlanSerializer(data=payload)
    if serializer.is_valid():
        serializer.save(user_id=user_id, uuid=payload['id'])
        logger.info(f'Created NutritionPlan (uuid={payload["id"]}) for user {user_id}')
        return None
    logger.warning(f'PowerSync nutritional plan create validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_update_plan(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PATCH event for a nutritional plan."""
    logger.debug(f'Received PowerSync payload for nutritional plan update: {payload}')
    try:
        entry = NutritionPlan.objects.get(uuid=payload['id'], user_id=user_id)
    except NutritionPlan.DoesNotExist:
        logger.warning(
            f'NutritionPlan with uuid {payload["id"]} and user {user_id} not found for update.'
        )
        return {
            'error': 'Not found',
            'details': f'NutritionPlan with uuid {payload["id"]} not found',
        }

    if not check_fk_ownership(payload, NutritionPlanViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'NutritionPlan references an object you do not own'}

    payload.pop('id', None)
    serializer = NutritionPlanSerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated NutritionPlan {entry.pk} (uuid={entry.uuid}) for user {user_id}')
        return None
    logger.warning(f'PowerSync nutritional plan update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_plan(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync DELETE event for a nutritional plan.

    Django's FK CASCADE removes all dependent meals, meal items and diary
    log entries in the same transaction.
    """
    logger.debug(f'Received PowerSync payload for nutritional plan delete: {payload}')
    try:
        entry = NutritionPlan.objects.get(uuid=payload['id'], user_id=user_id)
    except NutritionPlan.DoesNotExist:
        logger.warning(f'NutritionPlan with uuid {payload["id"]} not found for delete.')
        return {
            'error': 'Not found',
            'details': f'NutritionPlan with uuid {payload["id"]} not found',
        }
    entry.delete()
    logger.info(f'Deleted NutritionPlan (uuid={payload["id"]}) for user {user_id}')
    return None


#
# Meals
#


def handle_create_meal(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PUT event for a meal.

    The client generates the row's UUID; the parent plan is referenced by UUID
    too and resolved here. The `order` field is set to whatever the client
    computed (or 1 by default, matching the existing REST `perform_create`).
    """
    logger.debug(f'Received PowerSync payload for meal create: {payload}')

    error = resolve_uuid_fk(payload, 'plan', NutritionPlan)
    if error:
        return error

    if not check_fk_ownership(payload, MealViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'Meal references an object you do not own'}

    serializer = MealSerializer(data=payload)
    if serializer.is_valid():
        serializer.save(uuid=payload['id'], order=payload.get('order', 1))
        logger.info(f'Created Meal (uuid={payload["id"]}) for user {user_id}')
        return None
    logger.warning(f'PowerSync meal create validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_update_meal(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PATCH event for a meal."""
    logger.debug(f'Received PowerSync payload for meal update: {payload}')
    try:
        entry = Meal.objects.get(uuid=payload['id'], plan__user_id=user_id)
    except Meal.DoesNotExist:
        logger.warning(
            f'Meal with uuid {payload["id"]} and user {user_id} not found for update.'
        )
        return {'error': 'Not found', 'details': f'Meal with uuid {payload["id"]} not found'}

    error = resolve_uuid_fk(payload, 'plan', NutritionPlan)
    if error:
        return error

    if not check_fk_ownership(payload, MealViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'Meal references an object you do not own'}

    payload.pop('id', None)
    serializer = MealSerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated Meal {entry.pk} (uuid={entry.uuid}) for user {user_id}')
        return None
    logger.warning(f'PowerSync meal update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_meal(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync DELETE event for a meal.

    Django's FK CASCADE removes all dependent meal items in the same transaction.
    """
    logger.debug(f'Received PowerSync payload for meal delete: {payload}')
    try:
        entry = Meal.objects.get(uuid=payload['id'], plan__user_id=user_id)
    except Meal.DoesNotExist:
        logger.warning(f'Meal with uuid {payload["id"]} not found for delete.')
        return {'error': 'Not found', 'details': f'Meal with uuid {payload["id"]} not found'}
    entry.delete()
    logger.info(f'Deleted Meal (uuid={payload["id"]}) for user {user_id}')
    return None


#
# Meal items
#


def handle_create_mealitem(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PUT event for a meal item.

    The client generates the UUID and references its parent meal by UUID; the
    helper resolves that UUID to the integer FK before the serializer runs.
    """
    logger.debug(f'Received PowerSync payload for meal item create: {payload}')

    error = resolve_uuid_fk(payload, 'meal', Meal)
    if error:
        return error

    if not check_fk_ownership(payload, MealItemViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'MealItem references an object you do not own'}

    serializer = MealItemSerializer(data=payload)
    if serializer.is_valid():
        serializer.save(uuid=payload['id'], order=payload.get('order', 1))
        logger.info(f'Created MealItem (uuid={payload["id"]}) for user {user_id}')
        return None
    logger.warning(f'PowerSync meal item create validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_update_mealitem(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PATCH event for a meal item."""
    logger.debug(f'Received PowerSync payload for meal item update: {payload}')
    try:
        entry = MealItem.objects.get(uuid=payload['id'], meal__plan__user_id=user_id)
    except MealItem.DoesNotExist:
        logger.warning(
            f'MealItem with uuid {payload["id"]} and user {user_id} not found for update.'
        )
        return {'error': 'Not found', 'details': f'MealItem with uuid {payload["id"]} not found'}

    error = resolve_uuid_fk(payload, 'meal', Meal)
    if error:
        return error

    if not check_fk_ownership(payload, MealItemViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'MealItem references an object you do not own'}

    payload.pop('id', None)
    serializer = MealItemSerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated MealItem {entry.pk} (uuid={entry.uuid}) for user {user_id}')
        return None
    logger.warning(f'PowerSync meal item update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_mealitem(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync DELETE event for a meal item."""
    logger.debug(f'Received PowerSync payload for meal item delete: {payload}')
    try:
        entry = MealItem.objects.get(uuid=payload['id'], meal__plan__user_id=user_id)
    except MealItem.DoesNotExist:
        logger.warning(f'MealItem with uuid {payload["id"]} not found for delete.')
        return {'error': 'Not found', 'details': f'MealItem with uuid {payload["id"]} not found'}
    entry.delete()
    logger.info(f'Deleted MealItem (uuid={payload["id"]}) for user {user_id}')
    return None


#
# Log items (nutrition diary)
#


def handle_create_log(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PUT event for a diary log entry.

    Plan and meal FKs both arrive as UUID strings and are resolved to integer
    PKs before validation.
    """
    logger.debug(f'Received PowerSync payload for log create: {payload}')

    error = resolve_uuid_fk(payload, 'plan', NutritionPlan)
    if error:
        return error
    error = resolve_uuid_fk(payload, 'meal', Meal)
    if error:
        return error

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

    error = resolve_uuid_fk(payload, 'plan', NutritionPlan)
    if error:
        return error
    error = resolve_uuid_fk(payload, 'meal', Meal)
    if error:
        return error

    if not check_fk_ownership(payload, LogItemViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'LogItem references an object you do not own'}

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
