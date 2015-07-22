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
from django.core.urlresolvers import reverse_lazy, reverse

from wger.groups.models import Group
from wger.manager.tests.testcase import (
    WorkoutManagerTestCase,
    WorkoutManagerAccessTestCase,
    WorkoutManagerAddTestCase
)


class GroupUserJoinTestCase(WorkoutManagerTestCase):
    '''
    Tests different ways of joining a group
    '''

    def test_create_group(self):
        '''
        Creating a group joins the user and makes him an administrator
        '''
        self.user_login('test')
        response = self.client.post(reverse('groups:group:add'),
                                    {'name': 'Test group', 'description': 'Something clever'})
        group = Group.objects.get(pk=5)
        self.assertEqual(group.name, 'Test group')
        self.assertTrue(group.membership_set.filter(user__username='test', admin=True).exists())

    def join_public_group(self):
        '''
        Everybody can join a public group (helper function)
        '''
        group = Group.objects.get(pk=3)
        self.assertEqual(group.membership_set.count(), 0)
        self.client.get(reverse('groups:member:join-public', kwargs={'group_pk': 3}))
        self.assertEqual(group.membership_set.count(), 1)

    def test_join_public_group_1(self):
        self.user_login('admin')
        self.join_public_group()

    def test_join_public_group_1(self):
        self.user_login('test')
        self.join_public_group()


class GroupUserLeaveTestCase(WorkoutManagerTestCase):
    '''
    Tests different ways of leaving a group
    '''

    def test_leave_group(self):
        '''
        Leaving the group
        '''
        self.user_login('test')
        group = Group.objects.get(pk=2)
        self.assertEqual(group.membership_set.count(), 1)
        self.client.get(reverse('groups:member:leave', kwargs={'group_pk': 2}))
        self.assertEqual(group.membership_set.count(), 0)
