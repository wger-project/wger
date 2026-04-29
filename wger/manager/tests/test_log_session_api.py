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
import datetime

# Django
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import (
    WorkoutLog,
    WorkoutSession,
)
from wger.manager.powersync import (
    handle_create_log,
    handle_update_log,
)



OWN_SESSION = 'bbbbbbbb-bbbb-bbbb-bbbb-000000000001'
OWN_SESSION_OTHER_DATE = 'bbbbbbbb-bbbb-bbbb-bbbb-000000000002'
FOREIGN_SESSION = 'bbbbbbbb-bbbb-bbbb-bbbb-000000000005'
OWN_LOG = 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001'


class WorkoutLogSessionPinningRESTTestCase(WgerTestCase):
    """
    REST-API tests around pinning a log to an explicit session.

    The serializer must accept a writeable ``session`` field so that
    PowerSync (and any other client that owns the session UUID locally)
    can keep its log attached to the session it created. Foreign
    sessions must always be rejected at the viewset layer with a 403.

    Fixture references
    Users:
      1 = admin (own logs, own sessions, owns routine 1)
      2 = test  (foreign logs/sessions, owns routines 2/3)
    Sessions:
      bbbb…001 -> user=1, routine=1, date=2025-10-01
      bbbb…002 -> user=1, routine=1, date=2025-01-20
      bbbb…005 -> user=2, routine=3, date=2025-11-01
    Logs:
      aaaa…001 -> user=1, routine=1, session=bbbb…001
    """

    def setUp(self):
        super().setUp()
        self.user_login('admin')


    def test_create_log_with_explicit_own_session(self):
        """POST with an own session UUID pins the log to that session."""

        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'exercise': 1,
                'routine': 1,
                'session': OWN_SESSION_OTHER_DATE,
                'date': datetime.date(2025, 10, 1).isoformat(),
                'weight': 30,
                'repetitions': 8,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        log = WorkoutLog.objects.get(pk=response.json()['id'])
        # The explicit session must have been kept
        self.assertEqual(str(log.session_id), OWN_SESSION_OTHER_DATE)

    def test_create_log_with_foreign_session_rejected(self):
        """POST with a foreign session id must return 403 PermissionDenied."""

        before = WorkoutLog.objects.count()
        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'exercise': 1,
                'routine': 1,
                'session': FOREIGN_SESSION,
                'date': datetime.date(2025, 10, 1).isoformat(),
                'weight': 30,
                'repetitions': 8,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(WorkoutLog.objects.count(), before)

    def test_create_log_without_session_auto_creates(self):
        """POST without a session falls back to the legacy auto-create."""

        new_date = datetime.date(2030, 6, 15)
        before = WorkoutSession.objects.filter(
            user_id=1, routine_id=1, date=new_date
        ).count()
        self.assertEqual(before, 0)

        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'exercise': 1,
                'routine': 1,
                'date': new_date.isoformat(),
                'weight': 30,
                'repetitions': 8,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        log = WorkoutLog.objects.get(pk=response.json()['id'])
        self.assertIsNotNone(log.session_id)
        self.assertEqual(log.session.user_id, 1)
        self.assertEqual(log.session.date, new_date)

    def test_patch_log_with_foreign_session_rejected(self):
        """PATCH that tries to move a log onto a foreign session returns 403."""

        response = self.client.patch(
            reverse('workoutlog-detail', kwargs={'pk': OWN_LOG}),
            data={'session': FOREIGN_SESSION},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        log = WorkoutLog.objects.get(pk=OWN_LOG)
        # The original session must still be in place.
        self.assertEqual(str(log.session_id), OWN_SESSION)

    def test_patch_log_with_own_session_pins(self):
        """PATCH with an own session id repoints the log."""
        response = self.client.patch(
            reverse('workoutlog-detail', kwargs={'pk': OWN_LOG}),
            data={'session': OWN_SESSION_OTHER_DATE},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        log = WorkoutLog.objects.get(pk=OWN_LOG)
        self.assertEqual(str(log.session_id), OWN_SESSION_OTHER_DATE)


class WorkoutLogSessionPinningPowerSyncTestCase(WgerTestCase):
    """
    Same scenarios, but exercising the PowerSync upload handlers directly.
    """

    def test_create_log_with_explicit_own_session(self):
        before = WorkoutLog.objects.filter(session_id=OWN_SESSION_OTHER_DATE).count()
        result = handle_create_log(
            {
                'exercise': 1,
                'routine': 1,
                'session': OWN_SESSION_OTHER_DATE,
                'date': datetime.date(2025, 10, 1).isoformat(),
                'weight': 30,
                'repetitions': 8,
            },
            user_id=1,
        )
        self.assertIsNone(result)
        after = WorkoutLog.objects.filter(session_id=OWN_SESSION_OTHER_DATE).count()
        self.assertEqual(after, before + 1)

    def test_create_log_with_foreign_session_returns_forbidden(self):
        before = WorkoutLog.objects.count()
        result = handle_create_log(
            {
                'exercise': 1,
                'routine': 1,
                'session': FOREIGN_SESSION,
                'date': datetime.date(2025, 10, 1).isoformat(),
                'weight': 30,
                'repetitions': 8,
            },
            user_id=1,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.get('error'), 'Forbidden')
        self.assertEqual(WorkoutLog.objects.count(), before)

    def test_update_log_with_foreign_session_returns_forbidden(self):
        result = handle_update_log(
            {'id': OWN_LOG, 'session': FOREIGN_SESSION},
            user_id=1,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.get('error'), 'Forbidden')

        log = WorkoutLog.objects.get(pk=OWN_LOG)
        self.assertEqual(str(log.session_id), OWN_SESSION)

    def test_update_log_pins_own_session(self):
        result = handle_update_log(
            {'id': OWN_LOG, 'session': OWN_SESSION_OTHER_DATE},
            user_id=1,
        )
        self.assertIsNone(result)

        log = WorkoutLog.objects.get(pk=OWN_LOG)
        self.assertEqual(str(log.session_id), OWN_SESSION_OTHER_DATE)


class WorkoutLogSerializerSessionFilterTestCase(WgerTestCase):
    """
    Unit tests for ``OwnerScopedSessionField`` — the dynamic queryset on
    ``WorkoutLogSerializer.session`` must reject foreign sessions even
    when the upstream ``check_fk_ownership`` layer is not used.
    """

    def test_serializer_rejects_foreign_session_via_user_id_context(self):
        from wger.manager.api.serializers import WorkoutLogSerializer

        serializer = WorkoutLogSerializer(
            data={
                'exercise': 1,
                'routine': 1,
                'session': FOREIGN_SESSION,
                'date': datetime.date(2025, 10, 1).isoformat(),
                'weight': 30,
                'repetitions': 8,
            },
            context={'user_id': 1},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('session', serializer.errors)

    def test_serializer_accepts_own_session_via_user_id_context(self):
        from wger.manager.api.serializers import WorkoutLogSerializer

        serializer = WorkoutLogSerializer(
            data={
                'exercise': 1,
                'routine': 1,
                'session': OWN_SESSION,
                'date': datetime.date(2025, 10, 1).isoformat(),
                'weight': 30,
                'repetitions': 8,
            },
            context={'user_id': 1},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(str(serializer.validated_data['session'].pk), OWN_SESSION)

    def test_serializer_without_context_has_empty_session_queryset(self):
        """
        A serializer instantiated without any user context must not be
        able to resolve any session UUID — the queryset is empty by
        default, so the call falls through to a validation error.
        """
        from wger.manager.api.serializers import WorkoutLogSerializer

        serializer = WorkoutLogSerializer(
            data={
                'exercise': 1,
                'routine': 1,
                'session': OWN_SESSION,
                'date': datetime.date(2025, 10, 1).isoformat(),
                'weight': 30,
                'repetitions': 8,
            },
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('session', serializer.errors)
