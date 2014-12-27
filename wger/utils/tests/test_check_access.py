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

from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.utils.helpers import check_access, make_uid


class CheckAccessTestCase(WorkoutManagerTestCase):
    '''
    Test the "check_access" helper function
    '''

    def test_helper(self):
        '''
        Test the helper function
        '''

        user_share = User.objects.get(pk=1)
        uid_share = make_uid(1)
        self.assertTrue(user_share.userprofile.ro_access)

        user_no_share = User.objects.get(pk=2)
        uid_no_share = make_uid(2)
        self.assertFalse(user_no_share.userprofile.ro_access)

        anon = AnonymousUser()

        uid3 = make_uid(100)

        # Logged out user
        self.assertEqual(check_access(anon, uid_share), (False, user_share))
        self.assertFalse(check_access(anon, uid_no_share))
        self.assertRaises(Http404, check_access, anon, uid3)
        self.assertFalse(check_access(anon, 'not a UID'))
        self.assertFalse(check_access(anon))

        # Logged in user
        self.assertEqual(check_access(user_share, uid_share), (True, user_share))
        self.assertFalse(check_access(user_share, uid_no_share))
        self.assertEqual(check_access(user_share), (True, user_share))
        self.assertRaises(Http404, check_access, user_share, uid3)
        self.assertFalse(check_access(user_share, 'not a UID'))

        self.assertEqual(check_access(user_no_share, uid_share), (False, user_share))
        self.assertEqual(check_access(user_no_share, uid_no_share), (True, user_no_share))
        self.assertEqual(check_access(user_no_share), (True, user_no_share))
        self.assertRaises(Http404, check_access, user_no_share, uid3)
