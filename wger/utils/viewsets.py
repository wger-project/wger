# -*- coding: utf-8 -*-

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

# Third Party
from rest_framework import (
    exceptions,
    viewsets,
)


logger = logging.getLogger(__name__)


def check_fk_ownership(payload: dict, owner_objects: list[tuple], user_id: int) -> bool:
    """
    Validate that FK references in payload belong to the given user.

    Uses the same get_owner_object() convention as WgerOwnerObjectModelViewSet:
    owner_objects is a list of (Model, field_name) tuples. For each field present
    in payload, the referenced object is loaded and its ownership is verified via
    get_owner_object().user.

    Returns True if all checks pass, False otherwise.
    """
    for model_class, field_name in owner_objects:
        pk = payload.get(field_name)
        if pk is None:
            continue

        try:
            obj = model_class.objects.get(pk=pk)
        except model_class.DoesNotExist:
            logger.warning(f'{model_class.__name__} with pk {pk} not found during ownership check')
            return False

        owner = obj.get_owner_object()
        if owner and hasattr(owner, 'user') and owner.user_id != user_id:
            logger.warning(f'{model_class.__name__} {pk} does not belong to user {user_id}')
            return False
    return True


class WgerOwnerObjectModelViewSet(viewsets.ModelViewSet):
    """
    Custom viewset that makes sure the user can only create objects for himself
    """

    def _check_owner_permission(self, request):
        if not isinstance(request.data, dict):
            raise exceptions.ValidationError('Request data is not a dictionary')

        if not check_fk_ownership(request.data, self.get_owner_objects(), request.user.pk):
            raise exceptions.PermissionDenied('You are not allowed to do this')

    def create(self, request, *args, **kwargs):
        self._check_owner_permission(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._check_owner_permission(request)
        return super().update(request, *args, **kwargs)
