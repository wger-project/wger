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
