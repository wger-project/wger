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

import datetime

from django.contrib.auth.models import User

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.gym.helpers import get_user_last_activity
from wger.manager.models import WorkoutSession, WorkoutLog


class UserLastActivityTestCase(WorkoutManagerTestCase):
    '''
    Test the helper function for last user activity
    '''

    def test_user_last_activity(self):
        '''
        Test the helper function for last user activity
        '''
        self.user_login('admin')
        user = User.objects.get(username='admin')
        log = WorkoutLog.objects.get(pk=1)
        session = WorkoutSession.objects.get(pk=1)

        self.assertEqual(user.usercache.last_activity, datetime.date(2014, 1, 30))
        self.assertEqual(get_user_last_activity(user), datetime.date(2014, 1, 30))

        # Log more recent than session
        log.date = datetime.date(2014, 10, 2)
        log.save()
        session.date = datetime.date(2014, 10, 1)
        session.save()
        user = User.objects.get(username='admin')
        self.assertEqual(get_user_last_activity(user), datetime.date(2014, 10, 2))
        self.assertEqual(user.usercache.last_activity, datetime.date(2014, 10, 2))

        # Session more recent than log
        log.date = datetime.date(2014, 9, 1)
        log.save()
        session.date = datetime.date(2014, 10, 5)
        session.save()
        user = User.objects.get(username='admin')
        self.assertEqual(get_user_last_activity(user), datetime.date(2014, 10, 5))
        self.assertEqual(user.usercache.last_activity, datetime.date(2014, 10, 5))

        # No logs, but session
        WorkoutLog.objects.filter(user=user).delete()
        user = User.objects.get(username='admin')
        self.assertEqual(get_user_last_activity(user), datetime.date(2014, 10, 5))
        self.assertEqual(user.usercache.last_activity, datetime.date(2014, 10, 5))
