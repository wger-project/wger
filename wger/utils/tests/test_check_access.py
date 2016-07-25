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

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.utils.helpers import check_access


class CheckAccessTestCase(WorkoutManagerTestCase):
    '''
    Test the "check_access" helper function
    '''

    def test_helper(self):
        '''
        Test the helper function
        '''

        user_share = User.objects.get(pk=1)
        self.assertTrue(user_share.userprofile.ro_access)

        user_no_share = User.objects.get(pk=2)
        self.assertFalse(user_no_share.userprofile.ro_access)

        anon = AnonymousUser()

        # Logged out user
        self.assertEqual(check_access(anon, 'admin'), (False, user_share))
        self.assertRaises(Http404, check_access, anon, 'test')
        self.assertRaises(Http404, check_access, anon, 'not_a_username')
        self.assertRaises(Http404, check_access, anon)

        # Logged in user
        self.assertEqual(check_access(user_share, 'admin'), (True, user_share))
        self.assertRaises(Http404, check_access, user_share, 'test')
        self.assertEqual(check_access(user_share), (True, user_share))
        self.assertRaises(Http404, check_access, user_share, 'not_a_username')

        self.assertEqual(check_access(user_no_share, 'admin'), (False, user_share))
        self.assertEqual(check_access(user_no_share, 'test'), (True, user_no_share))
        self.assertEqual(check_access(user_no_share), (True, user_no_share))
        self.assertRaises(Http404, check_access, user_no_share, 'not_a_username')
