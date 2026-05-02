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

# Standard Library
import json

# Django
from django.contrib.auth.models import User

# Third Party
from rest_framework import status
from rest_framework.test import APITestCase

# wger
from wger.core.tests.base_testcase import BaseTestCase


POWERSYNC_URL = '/api/v2/upload-powersync-data'


class PowerSyncBaseTestCase(BaseTestCase, APITestCase):
    """
    Base test case for the PowerSync push handlers.
    """

    url = POWERSYNC_URL

    table = None
    """The PowerSync table name"""

    resource = None
    """The model under test. Used for count and ownership assertions."""

    user_access = 'test'
    """Username of the owner who is expected to succeed."""

    user_fail = 'admin'
    """A different user who must be rejected on cross-user writes."""

    pk_owned = None
    """
    Lookup id (uuid string or integer pk) of an entry owned by ``user_access``.
    Used by the update and delete mixins.
    """

    create_payload = None
    """Body for handle_create_*. Set to None to skip create tests."""

    update_payload = None
    """
    Body for handle_update_*. Must contain an ``id`` field that resolves to an
    object owned by ``user_access``. Set to None to skip update tests.
    """

    fk_ownership = ()
    """
    Iterable of (field_name, foreign_value) tuples used to verify that the
    handler rejects payloads referencing FKs owned by another user. Empty if the
    handler doesn't run a check_fk_ownership step.
    """

    def authenticate(self, username=None):
        user = User.objects.get(username=username or self.user_access)
        self.client.force_authenticate(user=user)

    def push(self, verb, payload):
        """Send a PowerSync push as the currently authenticated user."""
        body = json.dumps({'table': self.table, 'data': payload})
        return self.client.generic(verb, self.url, data=body, content_type='application/json')

    def get_owner_username(self, obj):
        return obj.get_owner_object().user.username


class PowerSyncCreateTestCase:
    """Mixin: ownership tests for handle_create_* (HTTP PUT)."""

    def _diff_new_object(self, pks_before):
        """Return the single object whose pk wasn't in ``pks_before``."""
        pks_after = set(self.resource.objects.values_list('pk', flat=True))
        new_pks = pks_after - pks_before
        self.assertEqual(
            len(new_pks), 1, f'Exactly one new {self.resource.__name__} row expected'
        )
        return self.resource.objects.get(pk=new_pks.pop())

    def test_create_anonymous_forbidden(self):
        if self.resource is None or self.create_payload is None:
            return
        before = self.resource.objects.count()
        response = self.push('PUT', self.create_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.resource.objects.count(), before)

    def test_create_owner_succeeds(self):
        if self.resource is None or self.create_payload is None:
            return
        self.authenticate()
        pks_before = set(self.resource.objects.values_list('pk', flat=True))
        response = self.push('PUT', self.create_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(response.json(), {'status': 'ok!'})

        new_obj = self._diff_new_object(pks_before)
        self.assertEqual(self.get_owner_username(new_obj), self.user_access)

    def test_create_preserves_client_supplied_id(self):
        """
        For tables where the client generates the row's primary key (UUID PK
        models), the server must store exactly that id rather than generate a
        new one — otherwise PowerSync's local copy and the server diverge.
        """
        if self.resource is None or self.create_payload is None:
            return
        if 'id' not in self.create_payload:
            return
        self.authenticate()
        pks_before = set(self.resource.objects.values_list('pk', flat=True))
        response = self.push('PUT', self.create_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        new_obj = self._diff_new_object(pks_before)
        self.assertEqual(
            str(new_obj.pk),
            str(self.create_payload['id']),
            'Server replaced the client-supplied id with a fresh one',
        )

    def test_create_ignores_user_in_payload(self):
        """A user/user_id smuggled in the payload must not change the owner."""
        if self.resource is None or self.create_payload is None:
            return
        other_user = User.objects.get(username=self.user_fail)
        payload = {**self.create_payload, 'user': other_user.pk, 'user_id': other_user.pk}

        self.authenticate()
        pks_before = set(self.resource.objects.values_list('pk', flat=True))
        response = self.push('PUT', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        new_obj = self._diff_new_object(pks_before)
        self.assertEqual(
            self.get_owner_username(new_obj),
            self.user_access,
            f'Created object should belong to {self.user_access}, not {self.user_fail}',
        )

    def test_create_fk_ownership_rejected(self):
        if self.resource is None or self.create_payload is None or not self.fk_ownership:
            return
        self.authenticate()
        for field, foreign_value in self.fk_ownership:
            payload = {**self.create_payload, field: foreign_value}
            before = self.resource.objects.count()
            response = self.push('PUT', payload)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            body = response.json()
            self.assertEqual(
                body.get('error'),
                'Forbidden',
                f'FK theft via {field}={foreign_value} should be rejected, got {body}',
            )
            self.assertEqual(
                self.resource.objects.count(),
                before,
                f'No row should be created when FK {field} is rejected',
            )


class PowerSyncUpdateTestCase:
    """Mixin: ownership tests for handle_update_* (HTTP PATCH)."""

    def _get_entry_for_update(self):
        """
        Return the model instance referenced by ``update_payload['id']``. The
        default tries pk first, then uuid. Subclasses with chained lookups
        (e.g. by ``plan__user_id``) can override.
        """
        ident = self.update_payload['id']
        try:
            return self.resource.objects.get(pk=ident)
        except (self.resource.DoesNotExist, ValueError, TypeError):
            return self.resource.objects.get(uuid=ident)

    def test_update_anonymous_forbidden(self):
        if self.resource is None or self.update_payload is None:
            return
        response = self.push('PATCH', self.update_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_owner_succeeds(self):
        if self.resource is None or self.update_payload is None:
            return
        self.authenticate()
        response = self.push('PATCH', self.update_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(response.json(), {'status': 'ok!'})

    def test_update_other_user_not_found(self):
        """A different user must not be able to PATCH someone else's row."""
        if self.resource is None or self.update_payload is None:
            return
        owned = self._get_entry_for_update()
        pk = owned.pk
        owner_before = self.get_owner_username(owned)

        self.authenticate(self.user_fail)
        response = self.push('PATCH', self.update_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(
            body.get('error'),
            'Not found',
            f'PATCH by foreign user should return Not found, got {body}',
        )

        # Re-fetch a fresh instance instead of refresh_from_db: the latter
        # forces ImageField models (gallery.Image) to recompute width/height
        # from a file that doesn't exist in the test environment.
        fresh = self.resource.objects.get(pk=pk)
        self.assertEqual(
            self.get_owner_username(fresh),
            owner_before,
            'Owner must not change after a rejected update',
        )

    def test_update_fk_ownership_rejected(self):
        if self.resource is None or self.update_payload is None or not self.fk_ownership:
            return
        self.authenticate()
        for field, foreign_value in self.fk_ownership:
            payload = {**self.update_payload, field: foreign_value}
            response = self.push('PATCH', payload)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            body = response.json()
            self.assertEqual(
                body.get('error'),
                'Forbidden',
                f'FK theft via {field}={foreign_value} should be rejected, got {body}',
            )


class PowerSyncCreateNotAllowedTestCase:
    """
    Mixin for tables where PUT (create) is explicitly rejected by the dispatcher
    because creation must go through the REST API (Routine, NutritionPlan,
    GalleryImage). PATCH and DELETE still work via PowerSync.
    """

    def test_create_method_not_allowed(self):
        if self.resource is None:
            return
        self.authenticate()
        before = self.resource.objects.count()
        response = self.push('PUT', self.create_payload or {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(
            body.get('error'),
            'Method not allowed',
            f'PUT to {self.table} should be rejected by the dispatcher, got {body}',
        )
        self.assertEqual(
            self.resource.objects.count(),
            before,
            'A rejected PUT must not create any rows',
        )


class PowerSyncDeleteTestCase:
    """Mixin: ownership tests for handle_delete_* (HTTP DELETE)."""

    def _delete_payload(self):
        return {'id': self.pk_owned}

    def test_delete_anonymous_forbidden(self):
        if self.resource is None or self.pk_owned is None:
            return
        before = self.resource.objects.count()
        response = self.push('DELETE', self._delete_payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.resource.objects.count(), before)

    def test_delete_other_user_not_found(self):
        if self.resource is None or self.pk_owned is None:
            return
        before = self.resource.objects.count()
        self.authenticate(self.user_fail)
        response = self.push('DELETE', self._delete_payload())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(
            body.get('error'),
            'Not found',
            f'DELETE by foreign user should return Not found, got {body}',
        )
        self.assertEqual(
            self.resource.objects.count(),
            before,
            'No row should be deleted on a rejected delete',
        )

    def test_delete_owner_succeeds(self):
        if self.resource is None or self.pk_owned is None:
            return
        before = self.resource.objects.count()
        self.authenticate()
        response = self.push('DELETE', self._delete_payload())
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(response.json(), {'status': 'ok!'})
        self.assertEqual(self.resource.objects.count(), before - 1)


class PowerSyncResourceTestCase(
    PowerSyncBaseTestCase,
    PowerSyncCreateTestCase,
    PowerSyncUpdateTestCase,
    PowerSyncDeleteTestCase,
):
    """
    Full CRUD bundle for tables that support PUT/PATCH/DELETE.

    Tables that don't support all verbs (Routine, NutritionPlan, Image only do
    PATCH/DELETE) should mix in only the relevant cases instead.
    """

    pass
