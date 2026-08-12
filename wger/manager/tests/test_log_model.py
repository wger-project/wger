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
import logging

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import (
    Slot,
    SlotEntry,
    WorkoutLog,
    WorkoutSession,
)


logger = logging.getLogger(__name__)


class LogModelTestCase(WgerTestCase):
    """
    Test some logic in the workout log model
    """

    def test_create_session(self):
        """
        Test that a new session is created if needed
        """

        WorkoutLog.objects.all().delete()
        WorkoutSession.objects.all().delete()

        self.assertEqual(WorkoutSession.objects.count(), 0)

        WorkoutLog(
            user_id=1,
            exercise_id=1,
            weight=10,
            repetitions=10,
        ).save()

        self.assertEqual(WorkoutSession.objects.count(), 1)

    def test_create_session_sets_day(self):
        """
        The auto-created session inherits the day of the log's slot entry, so
        that need_logs_to_advance days can find it
        """

        WorkoutLog.objects.all().delete()
        WorkoutSession.objects.all().delete()

        WorkoutLog(
            user_id=1,
            exercise_id=1,
            routine_id=1,
            slot_entry_id=1,
            weight=10,
            repetitions=10,
        ).save()

        session = WorkoutSession.objects.get()
        self.assertEqual(session.day_id, 1)

    def test_create_session_without_slot_entry_has_no_day(self):
        """
        A free log without a slot entry can't know its day
        """

        WorkoutLog.objects.all().delete()
        WorkoutSession.objects.all().delete()

        WorkoutLog(
            user_id=1,
            exercise_id=1,
            weight=10,
            repetitions=10,
        ).save()

        session = WorkoutSession.objects.get()
        self.assertIsNone(session.day_id)

    def test_fills_missing_day_on_a_client_created_session(self):
        """
        A session the client created without a day gets it from the log, so that
        need_logs_to_advance days can find it
        """

        session = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000001')
        self.assertIsNone(session.day_id)

        WorkoutLog(
            user_id=1,
            exercise_id=1,
            routine_id=1,
            slot_entry_id=1,
            session=session,
            weight=10,
            repetitions=10,
        ).save()

        session.refresh_from_db()
        self.assertEqual(session.day_id, 1)

    def test_does_not_overwrite_the_day_of_a_session(self):
        """
        A session that already has a day keeps it, even when the log points
        somewhere else
        """

        session = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000001')
        session.day_id = 3
        session.save(update_fields=['day'])

        WorkoutLog(
            user_id=1,
            exercise_id=1,
            routine_id=1,
            slot_entry_id=1,
            session=session,
            weight=10,
            repetitions=10,
        ).save()

        session.refresh_from_db()
        self.assertEqual(session.day_id, 3)

    def test_does_not_fill_the_day_when_the_logs_span_several_days(self):
        """
        A session whose logs come from more than one day stays without one, since
        no single day is the right answer
        """

        session = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000001')
        self.assertIsNone(session.day_id)

        # A second entry, on another day of the same routine
        other_slot = Slot.objects.create(day_id=3, order=1)
        other_entry = SlotEntry.objects.create(slot=other_slot, exercise_id=1, order=1)

        WorkoutLog(
            user_id=1,
            exercise_id=1,
            routine_id=1,
            slot_entry_id=1,
            session=session,
            weight=10,
            repetitions=10,
        ).save()

        session.refresh_from_db()
        self.assertEqual(session.day_id, 1)

        # The day of the first log is no longer the whole truth, but an already
        # set day is never taken away again
        WorkoutLog(
            user_id=1,
            exercise_id=1,
            routine_id=1,
            slot_entry=other_entry,
            session=session,
            weight=10,
            repetitions=10,
        ).save()

        session.refresh_from_db()
        self.assertEqual(session.day_id, 1)

    def test_does_not_fill_the_day_when_earlier_logs_disagree(self):
        """
        Logs that were already there decide as well, not just the one being saved
        """

        session = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000001')
        other_slot = Slot.objects.create(day_id=3, order=1)
        other_entry = SlotEntry.objects.create(slot=other_slot, exercise_id=1, order=1)

        # Two logs from different days, written without going through save()
        for slot_entry_id in (1, other_entry.pk):
            WorkoutLog.objects.bulk_create(
                [
                    WorkoutLog(
                        user_id=1,
                        exercise_id=1,
                        routine_id=1,
                        slot_entry_id=slot_entry_id,
                        session=session,
                        weight=10,
                        repetitions=10,
                    )
                ]
            )

        session.refresh_from_db()
        self.assertIsNone(session.day_id)

        WorkoutLog(
            user_id=1,
            exercise_id=1,
            routine_id=1,
            slot_entry_id=1,
            session=session,
            weight=20,
            repetitions=8,
        ).save()

        session.refresh_from_db()
        self.assertIsNone(session.day_id)

    def test_does_not_fill_the_day_from_another_routine(self):
        """
        The day of a slot entry from a different routine must not leak into the
        session
        """

        session = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000003')
        self.assertIsNone(session.day_id)
        self.assertEqual(session.routine_id, 2)

        # slot entry 1 lives in routine 1, the session in routine 2
        WorkoutLog(
            user_id=1,
            exercise_id=1,
            routine_id=1,
            slot_entry_id=1,
            session=session,
            weight=10,
            repetitions=10,
        ).save()

        session.refresh_from_db()
        self.assertIsNone(session.day_id)

    def test_save_reuses_session_when_duplicates_exist(self):
        """
        Duplicate routine-less sessions can exist for one (user, date) because the
        unique_together does not cover a NULL routine. A new log's save() must
        reuse an existing session instead of raising MultipleObjectsReturned.
        """
        WorkoutLog.objects.all().delete()
        WorkoutSession.objects.all().delete()

        # First log auto-creates a routine-less session for today.
        WorkoutLog(user_id=1, exercise_id=1, weight=10, repetitions=10).save()
        session = WorkoutSession.objects.get()
        self.assertIsNone(session.routine_id)

        # A duplicate (user, date, routine=None) — only possible because a NULL
        # routine escapes the unique_together guard.
        WorkoutSession.objects.create(user_id=1, date=session.date, routine=None)
        self.assertEqual(WorkoutSession.objects.count(), 2)

        # A second log for the same day must not crash and must not add a session.
        log = WorkoutLog(user_id=1, exercise_id=1, weight=20, repetitions=8)
        log.save()

        log.refresh_from_db()
        self.assertEqual(WorkoutSession.objects.count(), 2)
        existing_ids = set(WorkoutSession.objects.values_list('id', flat=True))
        self.assertIn(log.session_id, existing_ids)

    def test_dont_create_session_when_already_set(self):
        """
        If the log already has a (valid, own) session, the auto-create magic must
        not run and no extra session must be created.
        """

        initial_count = WorkoutSession.objects.count()
        self.assertEqual(initial_count, 5)

        log = WorkoutLog.objects.get(pk='aaaaaaaa-aaaa-aaaa-aaaa-000000000001')
        target = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000002')
        self.assertEqual(log.user_id, target.user_id)
        self.assertNotEqual(log.date.date(), target.date)

        log.session = target
        log.save()

        log.refresh_from_db()
        self.assertEqual(str(log.session_id), 'bbbbbbbb-bbbb-bbbb-bbbb-000000000002')
        self.assertEqual(WorkoutSession.objects.count(), initial_count)

    def test_keep_explicit_own_session(self):
        """
        When the client provides an explicit, matching session, save() must not
        replace it with a freshly created one.
        """

        log = WorkoutLog.objects.get(pk='aaaaaaaa-aaaa-aaaa-aaaa-000000000001')
        own_session = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000001')

        log.session = own_session
        log.weight = 99  # force a change
        log.save()

        log.refresh_from_db()
        self.assertEqual(str(log.session_id), 'bbbbbbbb-bbbb-bbbb-bbbb-000000000001')

    def test_session_ownership(self):
        """
        A log must never end up attached to another user's session, even if the
        caller tries to set ``log.session`` to a foreign one.
        """

        own_session = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000001')
        foreign_session = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000005')

        self.assertEqual(own_session.user_id, 1)
        self.assertEqual(foreign_session.user_id, 2)

        log = WorkoutLog.objects.get(pk='aaaaaaaa-aaaa-aaaa-aaaa-000000000001')
        self.assertEqual(log.user_id, 1)

        log.session = foreign_session
        log.save()

        log.refresh_from_db()
        self.assertNotEqual(log.session_id, foreign_session.pk)

        # Whatever session was assigned by the auto-create fallback must belong
        # to the same user as the log.
        self.assertEqual(log.session.user_id, log.user_id)

    def test_routine_ownership(self):
        """
        Test that the routine foreign key checks ownership
        """

        log = WorkoutLog.objects.get(pk='aaaaaaaa-aaaa-aaaa-aaaa-000000000001')
        log.routine_id = 3
        log.save()

        # Reload from db
        log = WorkoutLog.objects.get(pk='aaaaaaaa-aaaa-aaaa-aaaa-000000000001')

        self.assertEqual(log.routine_id, 1)

    def test_slot_entry_ownership(self):
        """
        Test that the slot_entry foreign key checks ownership at the
        model layer, parallel to the existing routine guard.

        SlotEntry pk=1 belongs to user 1; the new log is for user 2 with
        no routine. Without a guard, super().save() persists a row; with
        the guard, save() returns early and nothing is written.
        """

        log = WorkoutLog(
            user_id=2,
            exercise_id=1,
            slot_entry_id=1,
            repetitions=5,
            weight=50,
        )
        log.save()

        self.assertFalse(WorkoutLog.objects.filter(user_id=2, slot_entry_id=1).exists())

    def test_next_log_user_check_fail(self):
        """
        Test that the next log foreign key checks ownership
        """

        log2 = WorkoutLog.objects.get(pk='aaaaaaaa-aaaa-aaaa-aaaa-000000000002')
        log2.user_id = 2
        log2.save()

        log1 = WorkoutLog.objects.get(pk='aaaaaaaa-aaaa-aaaa-aaaa-000000000001')
        log1.user_id = 1
        log1.next_log = log2
        log1.save()

        self.assertEqual(log1.next_log, None)

    def test_next_log_user_check_success(self):
        """
        Test that the next log foreign key checks ownership
        """

        log1 = WorkoutLog.objects.get(pk='aaaaaaaa-aaaa-aaaa-aaaa-000000000001')
        log2 = WorkoutLog.objects.get(pk='aaaaaaaa-aaaa-aaaa-aaaa-000000000002')

        self.assertEqual(log1.user_id, 1)
        self.assertEqual(log2.user_id, 1)

        log1.next_log = log2
        log1.save()

        self.assertEqual(log1.next_log, log2)
