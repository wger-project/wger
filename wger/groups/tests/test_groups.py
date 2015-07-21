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

from wger.groups.models import Group
from wger.manager.tests.testcase import WorkoutManagerTestCase


class GroupAccessTestCase(WorkoutManagerTestCase):
    '''
    Test accessing a group page
    '''

    def test_access_public(self):
        '''
        Test accessing the detail page of a public group
        '''
        group = Group.objects.get(pk=1)

        # member
        self.user_login('admin')
        response = self.client.get(group.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # member
        self.user_login('test')
        response = self.client.get(group.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # not member
        self.user_login('trainer1')
        response = self.client.get(group.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # not logged in
        self.user_logout()
        response = self.client.get(group.get_absolute_url())
        self.assertEqual(response.status_code, 302)

    def test_access_private(self):
        '''
        Test accessing the detail page of a private group
        '''
        group = Group.objects.get(pk=2)

        # Not member
        self.user_login('admin')
        response = self.client.get(group.get_absolute_url())
        self.assertEqual(response.status_code, 403)

        # Member
        self.user_login('test')
        response = self.client.get(group.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # Not logged in
        self.user_logout()
        response = self.client.get(group.get_absolute_url())
        self.assertEqual(response.status_code, 302)
