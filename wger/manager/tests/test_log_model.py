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

    def test_dont_create_session(self):
        """
        Test that no session is created if the log already has one
        """

        self.assertEqual(WorkoutSession.objects.count(), 5)

        log = WorkoutLog.objects.get(pk=1)
        log.session_id = 1

        self.assertEqual(WorkoutSession.objects.count(), 5)

    def test_session_ownership(self):
        """
        Test that the session foreign key checks ownership
        """
        session1 = WorkoutSession.objects.get(pk=1)
        session5 = WorkoutSession.objects.get(pk=5)

        self.assertEqual(session1.user_id, 1)
        self.assertEqual(session5.user_id, 2)

        log = WorkoutLog.objects.get(pk=1)
        log.session = session5
        log.save()

        self.assertNotEqual(log.session_id, 4)

    def test_routine_ownership(self):
        """
        Test that the routine foreign key checks ownership
        """

        log = WorkoutLog.objects.get(pk=1)
        log.routine_id = 3
        log.save()

        # Reload from db
        log = WorkoutLog.objects.get(pk=1)

        self.assertEqual(log.routine_id, 1)

    def test_next_log_user_check_fail(self):
        """
        Test that the next log foreign key checks ownership
        """

        log2 = WorkoutLog.objects.get(pk=2)
        log2.user_id = 2
        log2.save()

        log1 = WorkoutLog.objects.get(pk=1)
        log1.user_id = 1
        log1.next_log = log2
        log1.save()

        self.assertEqual(log1.next_log, None)

    def test_next_log_user_check_success(self):
        """
        Test that the next log foreign key checks ownership
        """

        log1 = WorkoutLog.objects.get(pk=1)
        log2 = WorkoutLog.objects.get(pk=2)

        self.assertEqual(log1.user_id, 1)
        self.assertEqual(log2.user_id, 1)

        log1.next_log = log2
        log1.save()

        self.assertEqual(log1.next_log, log2)
