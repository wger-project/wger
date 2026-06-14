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

"""
Shared infrastructure for the PowerSync push handlers.

Each app declares one ``PowerSyncHandler`` subclass per synchronised table
and registers it via ``@register_handler``. The dispatcher in
``wger.core.api.views.upload_powersync_data`` looks up the handler by table
name and calls ``dispatch(http_verb, ...)``.
"""

# Standard Library
import logging
from typing import Any

# Django
from django.db.models import Model

# Third Party
from rest_framework.serializers import Serializer

# wger
from wger.utils.viewsets import check_fk_ownership


logger = logging.getLogger(__name__)


REGISTRY: dict[str, 'PowerSyncHandler'] = {}


class PowerSyncHandler:
    """
    Base class for PowerSync upload handlers.

    Subclasses set declarative attributes describing the table, model,
    serializer and ownership rules. The most common variations
    (``lookup_field``, ``user_filter``, FK-ownership viewset, serializer
    context, save kwargs, payload preprocessing) are all expressible via
    attributes or single-method overrides.
    """

    # Django model and DRF serializer for the table.
    model: type[Model] = None
    serializer_class: type[Serializer] = None

    # PowerSync table name. Populated by ``register_handler`` from
    # ``model._meta.db_table`` — the same value PowerSync sees in Postgres.
    table: str = ''

    # Set to a ViewSet class to enable check_fk_ownership against
    # ``ViewSetClass.get_owner_objects()``. Leave as None if the model has
    # no FKs that need ownership-validation (e.g. WeightEntry, Category).
    viewset_class = None

    # Lookup config for update/delete:
    #   Model.objects.get(<lookup_field>=payload['id'], <user_filter>=user_id)
    # ``lookup_field`` is 'pk' (most models) or 'uuid' (WeightEntry).
    # ``user_filter`` is 'user_id' for direct ownership or a chained lookup
    # like 'plan__user_id' / 'meal__plan__user_id' / 'category__user_id'.
    lookup_field: str = 'pk'
    user_filter: str = 'user_id'

    # Set to False for tables where creation must go through REST (Routine,
    # Image). The dispatcher then returns "Method not allowed" instead of
    # running the create handler.
    supports_create: bool = True

    # Set to False for tables that must never be deleted through PowerSync
    # (UserProfile). handle_delete then returns "Method not allowed" instead
    # of deleting the row.
    supports_delete: bool = True

    # If True, the handler passes ``user_id`` into the serializer context so
    # that owner-scoped fields (e.g. WorkoutLogSerializer.session) can filter
    # their queryset.
    pass_user_id_in_context: bool = False

    @property
    def label(self) -> str:
        """Human-readable model name used in log lines and error details."""
        return self.model.__name__

    #
    # Hooks
    #

    def preprocess_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Last-chance mutation of the payload before validation. Default is a
        no-op; gallery uses this to drop the binary ``image`` field that only
        REST is allowed to write.
        """
        return payload

    def create_save_kwargs(self, payload: dict[str, Any], user_id: int) -> dict[str, Any]:
        """
        kwargs forwarded to ``serializer.save()`` on create. Default forces the
        owning user. Override for client-supplied UUID PKs (WeightEntry),
        ordering (Meal/MealItem) or models that don't take ``user_id`` because
        ownership rides on a FK chain (LogItem, MealItem).
        """
        return {'user_id': user_id}

    #
    # Public CRUD entry points
    #

    def handle_create(self, payload: dict[str, Any], user_id: int) -> dict | None:
        if not self.supports_create:
            return {
                'error': 'Method not allowed',
                'details': f'{self.label} creation must go through the REST API',
            }

        logger.debug(f'Received PowerSync payload for {self.label} create: {payload}')
        payload = self.preprocess_payload(payload)

        fk_err = self._check_fk(payload, user_id)
        if fk_err is not None:
            return fk_err

        serializer = self.serializer_class(
            data=payload,
            context=self._serializer_context(user_id),
        )
        if serializer.is_valid():
            serializer.save(**self.create_save_kwargs(payload, user_id))
            logger.debug(f'Created {self.label} {payload.get("id")} for user {user_id}')
            return None
        return self._validation_failed(serializer.errors)

    def handle_update(self, payload: dict[str, Any], user_id: int) -> dict | None:
        logger.debug(f'Received PowerSync payload for {self.label} update: {payload}')
        payload = self.preprocess_payload(payload)

        entry = self._get_or_none(payload, user_id)
        if entry is None:
            return self._not_found(payload['id'])

        fk_err = self._check_fk(payload, user_id)
        if fk_err is not None:
            return fk_err

        serializer = self.serializer_class(
            entry,
            data=payload,
            partial=True,
            context=self._serializer_context(user_id),
        )
        if serializer.is_valid():
            serializer.save()
            logger.debug(f'Updated {self.label} {entry.pk} for user {user_id}')
            return None
        return self._validation_failed(serializer.errors)

    def handle_delete(self, payload: dict[str, Any], user_id: int) -> dict | None:
        if not self.supports_delete:
            return {
                'error': 'Method not allowed',
                'details': f'{self.label} cannot be deleted',
            }

        logger.debug(f'Received PowerSync payload for {self.label} delete: {payload}')
        entry = self._get_or_none(payload, user_id)
        if entry is None:
            return self._not_found(payload['id'])
        entry.delete()
        logger.debug(f'Deleted {self.label} {payload["id"]} for user {user_id}')
        return None

    def dispatch(
        self,
        http_verb: str,
        payload: dict[str, Any],
        user_id: int,
    ) -> dict | None:
        """Route an HTTP verb to the matching CRUD handler."""
        if http_verb == 'PUT':
            return self.handle_create(payload, user_id)
        if http_verb == 'PATCH':
            return self.handle_update(payload, user_id)
        if http_verb == 'DELETE':
            return self.handle_delete(payload, user_id)
        return {'error': 'Method not allowed', 'details': f'Unsupported HTTP verb: {http_verb}'}

    #
    # Internals
    #

    def _serializer_context(self, user_id: int) -> dict[str, Any]:
        if self.pass_user_id_in_context:
            return {'user_id': user_id}
        return {}

    def _check_fk(self, payload: dict[str, Any], user_id: int) -> dict | None:
        if self.viewset_class is None:
            return None
        if check_fk_ownership(payload, self.viewset_class.get_owner_objects(), user_id):
            return None
        return {
            'error': 'Forbidden',
            'details': f'{self.label} references an object you do not own',
        }

    def _get_or_none(self, payload: dict[str, Any], user_id: int):
        ident = payload['id']
        try:
            return self.model.objects.get(**{self.lookup_field: ident, self.user_filter: user_id})
        except self.model.DoesNotExist:
            return None

    def _not_found(self, ident) -> dict:
        msg = f'{self.label} with id {ident} not found'
        logger.warning(msg)
        return {'error': 'Not found', 'details': msg}

    def _validation_failed(self, errors) -> dict:
        logger.warning(f'PowerSync {self.label} validation failed: {errors}')
        return {'error': 'Validation failed', 'details': errors}


def register_handler(cls: type[PowerSyncHandler]) -> type[PowerSyncHandler]:
    """
    Class decorator: instantiate ``cls`` and add the singleton to ``REGISTRY``
    keyed by the model's DB table name (which is what the PowerSync sync rules
    expose).
    """
    if cls.model is None:
        raise ValueError(f'{cls.__name__} must set `model`')
    cls.table = cls.model._meta.db_table
    if cls.table in REGISTRY:
        raise ValueError(
            f'PowerSync handler for table "{cls.table}" is already registered '
            f'(by {type(REGISTRY[cls.table]).__name__})'
        )
    REGISTRY[cls.table] = cls()
    return cls
