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
from wger.measurements.api.serializers import (
    CategorySerializer,
    MeasurementSerializer,
)
from wger.measurements.api.views import MeasurementViewSet
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.utils.viewsets import check_fk_ownership


logger = logging.getLogger(__name__)


#
# Categories
#


def handle_create_category(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PUT event for a measurement category."""
    logger.debug(f'Received PowerSync payload for category create: {payload}')
    serializer = CategorySerializer(data=payload)
    if serializer.is_valid():
        serializer.save(user_id=user_id)
        logger.info(f'Created Category {payload["id"]} for user {user_id}')
        return None
    logger.warning(f'PowerSync category create validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_update_category(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PATCH event for a measurement category."""
    logger.debug(f'Received PowerSync payload for category update: {payload}')
    try:
        entry = Category.objects.get(pk=payload['id'], user_id=user_id)
    except Category.DoesNotExist:
        logger.warning(f'Category {payload["id"]} for user {user_id} not found for update.')
        return {'error': 'Not found', 'details': f'Category {payload["id"]} not found'}

    serializer = CategorySerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated Category {entry.pk} for user {user_id}')
        return None
    logger.warning(f'PowerSync category update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_category(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync DELETE event for a measurement category.

    Django's FK CASCADE removes any dependent measurements in the same
    transaction.
    """
    logger.debug(f'Received PowerSync payload for category delete: {payload}')
    try:
        entry = Category.objects.get(pk=payload['id'], user_id=user_id)
    except Category.DoesNotExist:
        logger.warning(f'Category {payload["id"]} not found for delete.')
        return {'error': 'Not found', 'details': f'Category {payload["id"]} not found'}
    entry.delete()
    logger.info(f'Deleted Category {payload["id"]} for user {user_id}')
    return None


#
# Measurements
#


def handle_create_measurement(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PUT event for a measurement."""
    logger.debug(f'Received PowerSync payload for measurement create: {payload}')

    if not check_fk_ownership(payload, MeasurementViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'Measurement references a category you do not own'}

    serializer = MeasurementSerializer(data=payload)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Created Measurement {payload["id"]} for user {user_id}')
        return None
    logger.warning(f'PowerSync measurement create validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_update_measurement(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync PATCH event for a measurement."""
    logger.debug(f'Received PowerSync payload for measurement update: {payload}')
    try:
        entry = Measurement.objects.get(pk=payload['id'], category__user_id=user_id)
    except Measurement.DoesNotExist:
        logger.warning(
            f'Measurement {payload["id"]} for user {user_id} not found for update.'
        )
        return {'error': 'Not found', 'details': f'Measurement {payload["id"]} not found'}

    if not check_fk_ownership(payload, MeasurementViewSet.get_owner_objects(), user_id):
        return {'error': 'Forbidden', 'details': 'Measurement references a category you do not own'}

    serializer = MeasurementSerializer(entry, data=payload, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Updated Measurement {entry.pk} for user {user_id}')
        return None
    logger.warning(f'PowerSync measurement update validation failed: {serializer.errors}')
    return {'error': 'Validation failed', 'details': serializer.errors}


def handle_delete_measurement(payload: dict[str, Any], user_id: int) -> dict | None:
    """Handle a PowerSync DELETE event for a measurement."""
    logger.debug(f'Received PowerSync payload for measurement delete: {payload}')
    try:
        entry = Measurement.objects.get(pk=payload['id'], category__user_id=user_id)
    except Measurement.DoesNotExist:
        logger.warning(f'Measurement {payload["id"]} not found for delete.')
        return {'error': 'Not found', 'details': f'Measurement {payload["id"]} not found'}
    entry.delete()
    logger.info(f'Deleted Measurement {payload["id"]} for user {user_id}')
    return None
