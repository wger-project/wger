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
            reps=10,
        ).save()

        self.assertEqual(WorkoutSession.objects.count(), 1)

    def test_dont_create_session(self):
        """
        Test that no session is created if the log already has one
        """

        self.assertEqual(WorkoutSession.objects.count(), 4)

        log = WorkoutLog.objects.get(pk=1)
        log.session_id = 1

        self.assertEqual(WorkoutSession.objects.count(), 4)
