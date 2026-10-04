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
from decimal import Decimal

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.base_testcase import WgerTestCase, get_field_snapshot
from wger.manager.models import Day, Routine, Slot, SlotEntry, WorkoutLog, WorkoutSession


class WorkoutHistoryRetentionTestCase(WgerTestCase):
    def setUp(self):
        super().setUp()
        self.user_login('test')
        self.owner = User.objects.get(username='test')
        self.routine = Routine.objects.create(
            user=self.owner,
            name='History retention',
            start=datetime.date(2026, 1, 1),
            end=datetime.date(2026, 2, 1),
        )
        self.day = Day.objects.create(routine=self.routine, name='Training day')
        self.slot = Slot.objects.create(day=self.day)
        self.entry = SlotEntry.objects.create(slot=self.slot, exercise_id=1)
        self.session = WorkoutSession.objects.create(
            user=self.owner, routine=self.routine, day=self.day
        )
        self.log = WorkoutLog.objects.create(
            user=self.owner,
            exercise_id=1,
            routine=self.routine,
            slot_entry=self.entry,
            session=self.session,
            iteration=1,
            weight=Decimal('25'),
            weight_target=Decimal('30'),
            repetitions=8,
            repetitions_target=10,
        )

    def assert_history_preserved(
        self, endpoint, instance, *, routine_deleted=False, day_deleted=False
    ):
        log_values = get_field_snapshot(self.log)
        session_values = get_field_snapshot(self.session)
        log_count = WorkoutLog.objects.count()
        session_count = WorkoutSession.objects.count()
        response = self.client.delete(reverse(endpoint, kwargs={'pk': instance.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.content)
        self.assertFalse(type(instance).objects.filter(pk=instance.pk).exists())

        self.log.refresh_from_db()
        self.session.refresh_from_db()
        log_values['slot_entry_id'] = None
        if routine_deleted:
            log_values['routine_id'] = None
            session_values['routine_id'] = None
        if day_deleted:
            session_values['day_id'] = None
        self.assertEqual(get_field_snapshot(self.log), log_values)
        self.assertEqual(get_field_snapshot(self.session), session_values)
        self.assertEqual(WorkoutLog.objects.count(), log_count)
        self.assertEqual(WorkoutSession.objects.count(), session_count)

        for name, obj in [('workoutlog-detail', self.log), ('workoutsession-detail', self.session)]:
            response = self.client.get(reverse(name, kwargs={'pk': obj.pk}))
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
            self.assertEqual(
                response.json()['routine'], None if routine_deleted else self.routine.pk
            )

    def test_delete_slot_entry_preserves_history(self):
        self.assert_history_preserved('slot-entry-detail', self.entry)

    def test_delete_slot_preserves_history(self):
        self.assert_history_preserved('slot-detail', self.slot)

    def test_delete_day_preserves_history(self):
        self.assert_history_preserved('day-detail', self.day, day_deleted=True)

    def test_delete_routine_preserves_history(self):
        self.assert_history_preserved(
            'routine-detail', self.routine, routine_deleted=True, day_deleted=True
        )

    def test_bulk_delete_routine_preserves_history(self):
        Routine.objects.filter(pk=self.routine.pk).delete()
        self.log.refresh_from_db()
        self.session.refresh_from_db()
        self.assertIsNone(self.log.routine_id)
        self.assertIsNone(self.log.slot_entry_id)
        self.assertIsNone(self.session.routine_id)
        self.assertIsNone(self.session.day_id)
        self.assertEqual(self.log.session_id, self.session.pk)

    def test_foreign_user_cannot_delete_routine_or_read_retained_history(self):
        self.user_login('admin')
        response = self.client.delete(reverse('routine-detail', kwargs={'pk': self.routine.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Routine.objects.filter(pk=self.routine.pk).exists())

        self.routine.delete()
        self.assertTrue(WorkoutLog.objects.filter(pk=self.log.pk).exists())
        for endpoint, obj in [
            ('workoutlog-detail', self.log),
            ('workoutsession-detail', self.session),
        ]:
            response = self.client.get(reverse(endpoint, kwargs={'pk': obj.pk}))
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_explicit_session_deletion_still_removes_its_logs(self):
        response = self.client.delete(
            reverse('workoutsession-detail', kwargs={'pk': self.session.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(WorkoutLog.objects.filter(pk=self.log.pk).exists())
        self.assertTrue(Routine.objects.filter(pk=self.routine.pk).exists())

    def test_account_deletion_still_removes_history(self):
        self.owner.delete()
        self.assertFalse(WorkoutLog.objects.filter(pk=self.log.pk).exists())
        self.assertFalse(WorkoutSession.objects.filter(pk=self.session.pk).exists())
