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
from django.contrib.auth.models import User
from django.utils import timezone

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.gym.helpers import get_user_last_activity
from wger.manager.models import (
    WorkoutLog,
    WorkoutSession,
)


class UserLastActivityTestCase(WgerTestCase):
    """
    Test the helper function for last user activity

    TODO: check if we want to get rid of usercache.last_activity
    """

    def setUp(self):
        super().setUp()

        self.user = User.objects.get(username='admin')

        # Start from a clean slate, the fixtures have both logs and sessions
        WorkoutLog.objects.filter(user=self.user).delete()
        WorkoutSession.objects.filter(user=self.user).delete()

    def add_log(self, date: datetime.date):
        WorkoutLog(
            user=self.user,
            exercise_id=1,
            routine_id=1,
            weight=80,
            repetitions=5,
            date=timezone.make_aware(datetime.datetime.combine(date, datetime.time(12, 0))),
        ).save()

    def add_session(self, date: datetime.date):
        WorkoutSession(user=self.user, routine_id=1, date=date).save()

    def test_no_activity(self):
        self.assertIsNone(get_user_last_activity(self.user))

    def test_only_logs(self):
        self.add_log(datetime.date(2024, 3, 1))
        self.add_log(datetime.date(2024, 3, 5))

        self.assertEqual(get_user_last_activity(self.user), datetime.date(2024, 3, 5))

    def test_only_sessions(self):
        """
        Users that only track sessions are active too
        """
        self.add_session(datetime.date(2024, 3, 7))

        self.assertEqual(get_user_last_activity(self.user), datetime.date(2024, 3, 7))

    def test_log_more_recent_than_session(self):
        self.add_log(datetime.date(2024, 3, 10))
        self.add_session(datetime.date(2024, 3, 2))

        self.assertEqual(get_user_last_activity(self.user), datetime.date(2024, 3, 10))

    def test_session_more_recent_than_log(self):
        self.add_log(datetime.date(2024, 3, 2))
        self.add_session(datetime.date(2024, 3, 10))

        self.assertEqual(get_user_last_activity(self.user), datetime.date(2024, 3, 10))
