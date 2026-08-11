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
import logging

# Django
from django.test import override_settings
from django.utils import timezone

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import (
    WorkoutLog,
    WorkoutSession,
)


logger = logging.getLogger(__name__)


class LogSessionMatchingTestCase(WgerTestCase):
    """
    Test which session a log without an explicit one is attached to
    """

    def setUp(self):
        super().setUp()
        WorkoutLog.objects.all().delete()
        WorkoutSession.objects.all().delete()

    @staticmethod
    def make_session(start, end=None):
        return WorkoutSession.objects.create(
            user_id=1,
            routine_id=1,
            datetime_start=timezone.make_aware(datetime.datetime(*start)),
            datetime_end=timezone.make_aware(datetime.datetime(*end)) if end else None,
        )

    @staticmethod
    def make_log(date):
        log = WorkoutLog(
            user_id=1,
            routine_id=1,
            exercise_id=1,
            weight=10,
            repetitions=10,
            date=timezone.make_aware(datetime.datetime(*date)),
        )
        log.save()
        return log

    def test_log_inside_a_session_over_midnight(self):
        """A log after midnight belongs to the session that started the evening before"""

        session = self.make_session((2025, 3, 10, 23, 0), (2025, 3, 11, 1, 0))
        log = self.make_log((2025, 3, 11, 0, 30))

        self.assertEqual(log.session_id, session.pk)
        self.assertEqual(WorkoutSession.objects.count(), 1)

    def test_log_joins_an_open_session(self):
        """A log within the window of a session without an end joins it"""

        session = self.make_session((2025, 3, 10, 23, 0))
        log = self.make_log((2025, 3, 11, 1, 0))

        self.assertEqual(log.session_id, session.pk)

    def test_the_most_recent_open_session_wins(self):
        """With several open sessions in the window the newest one gets the log"""

        self.make_session((2025, 3, 10, 8, 0))
        newer = self.make_session((2025, 3, 10, 11, 0))
        log = self.make_log((2025, 3, 10, 12, 0))

        self.assertEqual(log.session_id, newer.pk)

    def test_a_covering_session_wins_over_an_open_one(self):
        """A session the log falls into beats a more recent open session"""

        covering = self.make_session((2025, 3, 10, 9, 0), (2025, 3, 10, 13, 0))
        self.make_session((2025, 3, 10, 11, 0))
        log = self.make_log((2025, 3, 10, 12, 0))

        self.assertEqual(log.session_id, covering.pk)

    def test_log_outside_the_window_starts_a_new_session(self):
        """A log too long after an open session gets one of its own"""

        session = self.make_session((2025, 3, 10, 10, 0))
        log = self.make_log((2025, 3, 10, 16, 0))

        self.assertNotEqual(log.session_id, session.pk)
        self.assertEqual(WorkoutSession.objects.count(), 2)

    @override_settings(WGER_MAX_SESSION_LENGTH_HOURS=8)
    def test_the_window_follows_the_setting(self):
        """The same log joins the session once the window is wide enough"""

        session = self.make_session((2025, 3, 10, 10, 0))
        log = self.make_log((2025, 3, 10, 16, 0))

        self.assertEqual(log.session_id, session.pk)

    def test_log_after_a_closed_session_starts_a_new_one(self):
        """A closed session is not extended, even within the window"""

        session = self.make_session((2025, 3, 10, 10, 0), (2025, 3, 10, 11, 0))
        log = self.make_log((2025, 3, 10, 12, 0))

        self.assertNotEqual(log.session_id, session.pk)
        self.assertEqual(WorkoutSession.objects.count(), 2)


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
        WorkoutSession.objects.create(
            user_id=1, datetime_start=session.datetime_start, routine=None
        )
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
        self.assertNotEqual(log.date.date(), target.datetime_start.date())

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
