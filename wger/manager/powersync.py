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
from wger.manager.api.serializers import (
    RoutineSerializer,
    WorkoutLogSerializer,
    WorkoutSessionSerializer,
)
from wger.manager.api.views import (
    RoutineViewSet,
    WorkoutLogViewSet,
    WorkoutSessionViewSet,
)
from wger.manager.models import (
    Routine,
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.viewsets import check_fk_ownership


logger = logging.getLogger(__name__)


def handle_update_log(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a push event from PowerSync"""
    logger.debug(f'Received PowerSync payload for update: {payload}')
    try:
        entry = WorkoutLog.objects.get(pk=payload['id'], user_id=user_id)
    except WorkoutLog.DoesNotExist:
        logger.warning(
            f'WorkoutLog with UUID {payload["id"]} and user {user_id} not found for update.'
        )
        return {'error': 'Not found', 'details': f'WorkoutLog with UUID {payload["id"]} not found'}

    if not check_fk_ownership(payload, WorkoutLogViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'WorkoutLog references an object you do not own'}

    serializer = WorkoutLogSerializer(
        entry, data=payload, partial=True, context={'user_id': user_id}
    )
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated WorkoutLog {entry.pk} for user {user_id}')
        return None
    logger.warning(f'PowerSync update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_create_log(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a create event from PowerSync"""
    logger.debug(f'Received PowerSync payload for create: {payload}')

    if not check_fk_ownership(payload, WorkoutLogViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'WorkoutLog references an object you do not own'}

    serializer = WorkoutLogSerializer(data=payload, context={'user_id': user_id})
    if serializer.is_valid():
        serializer.save(user_id=user_id)
        return None
    logger.warning(f'PowerSync create validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_log(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a delete event from PowerSync"""
    logger.debug(f'Received PowerSync payload for delete: {payload}')
    try:
        entry = WorkoutLog.objects.get(pk=payload['id'], user_id=user_id)
    except WorkoutLog.DoesNotExist:
        logger.warning(f'WorkoutLog with UUID {payload["id"]} not found for delete.')
        return {'error': 'Not found', 'details': f'WorkoutLog with UUID {payload["id"]} not found'}
    entry.delete()
    return None


def handle_update_session(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a push event from PowerSync"""
    logger.debug(f'Received PowerSync payload for update: {payload}')
    try:
        entry = WorkoutSession.objects.get(pk=payload['id'], user_id=user_id)
    except WorkoutSession.DoesNotExist:
        logger.warning(
            f'WorkoutSession with UUID {payload["id"]} and user {user_id} not found for update.'
        )
        return {
            'error': 'Not found',
            'details': f'WorkoutSession with UUID {payload["id"]} not found',
        }

    if not check_fk_ownership(payload, WorkoutSessionViewSet.get_owner_objects(), user_id):
        return {
            'error': 'Forbidden',
            'details': 'WorkoutSession references an object you do not own',
        }

    serializer = WorkoutSessionSerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated WorkoutSession {entry.pk} for user {user_id}')
        return None
    logger.warning(f'PowerSync update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_create_session(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a create event from PowerSync"""
    logger.debug(f'Received PowerSync payload for create: {payload}')

    if not check_fk_ownership(payload, WorkoutSessionViewSet.get_owner_objects(), user_id):
        return {
            'error': 'Forbidden',
            'details': 'WorkoutSession references an object you do not own',
        }

    serializer = WorkoutSessionSerializer(data=payload)
    if serializer.is_valid():
        serializer.save(user_id=user_id)
        return None
    logger.warning(f'PowerSync create validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_session(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a delete event from PowerSync"""
    logger.debug(f'Received PowerSync payload for delete: {payload}')
    try:
        entry = WorkoutSession.objects.get(pk=payload['id'], user_id=user_id)
    except WorkoutSession.DoesNotExist:
        logger.warning(f'WorkoutSession with UUID {payload["id"]} not found for delete.')
        return {
            'error': 'Not found',
            'details': f'WorkoutSession with UUID {payload["id"]} not found',
        }
    entry.delete()
    return None


def handle_update_routine(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PATCH event for a routine.

    Creation still goes through REST (the backend assigns the integer PK and
    `created` timestamp), so there is no `handle_create_routine` here — only
    edit and delete are part of the PowerSync upload pipeline.
    """
    logger.debug(f'Received PowerSync payload for routine update: {payload}')
    try:
        entry = Routine.objects.get(pk=payload['id'], user_id=user_id)
    except Routine.DoesNotExist:
        logger.warning(
            f'Routine with id {payload["id"]} and user {user_id} not found for update.'
        )
        return {
            'error': 'Not found',
            'details': f'Routine with id {payload["id"]} not found',
        }

    if not check_fk_ownership(payload, RoutineViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'Routine references an object you do not own'}

    serializer = RoutineSerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated Routine {entry.pk} for user {user_id}')
        return None
    logger.warning(f'PowerSync routine update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_routine(payload: dict[str, Any], user_id: int) -> dict | None:
    """
    Handle a PowerSync DELETE event for a routine.

    Django's FK CASCADE removes all dependent days, slots, set configs,
    sessions and logs in the same transaction.
    """
    logger.debug(f'Received PowerSync payload for routine delete: {payload}')
    try:
        entry = Routine.objects.get(pk=payload['id'], user_id=user_id)
    except Routine.DoesNotExist:
        logger.warning(f'Routine with id {payload["id"]} not found for delete.')
        return {
            'error': 'Not found',
            'details': f'Routine with id {payload["id"]} not found',
        }
    entry.delete()
    logger.info(f'Deleted Routine {payload["id"]} for user {user_id}')
    return None
