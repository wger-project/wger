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
# Django
from django.contrib.auth.models import User
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.groups.models import Group


class GroupUserJoinTestCase(WgerTestCase):
    """
    Tests different ways of joining a group
    """

    def test_create_group(self):
        """
        Creating a group joins the user and makes him an administrator
        """
        self.user_login('test')
        user = User.objects.get(username='test')
        self.assertTrue(user.userprofile.gym)

        self.client.post(reverse('groups:group:add'),
                         {'name': 'Test group', 'description': 'Something clever'})
        group = Group.objects.get(pk=Group.objects.latest('id').id)
        self.assertEqual(group.name, 'Test group')
        self.assertTrue(group.membership_set.filter(user__username='test', admin=True).exists())
        self.assertEqual(group.gym_id, 1)

    def test_create_group_no_gym(self):
        """
        Creating a group joins the user and makes him an administrator

        If the user doesn't belong to a gym, the group's gym reference is not set
        """
        user = User.objects.get(username='test')
        user.userprofile.gym = None
        user.userprofile.save()

        self.user_login('test')
        self.client.post(reverse('groups:group:add'),
                         {'name': 'Test group', 'description': 'Something clever'})
        group = Group.objects.get(pk=Group.objects.latest('id').id)
        self.assertEqual(group.name, 'Test group')
        self.assertFalse(group.gym)

    def join_public_group(self):
        """
        Everybody can join a public group (helper function)
        """
        group = Group.objects.get(pk=4)
        self.assertEqual(group.membership_set.count(), 0)
        self.client.get(reverse('groups:member:join-public', kwargs={'group_pk': 4}))
        self.assertEqual(group.membership_set.count(), 1)

    def test_join_public_group_admin(self):
        """
        Join public group as user admin
        """
        self.user_login('admin')
        self.join_public_group()

    def test_join_public_group_test(self):
        """
        Join public group as user test
        """
        self.user_login('test')
        self.join_public_group()


class GroupUserLeaveTestCase(WgerTestCase):
    """
    Tests different ways of leaving a group
    """

    def test_leave_group_own(self):
        """
        User leaves a group he is a member of
        """
        self.user_login('test')
        group = Group.objects.get(pk=2)
        self.assertEqual(group.membership_set.count(), 2)
        self.client.get(reverse('groups:member:leave', kwargs={'group_pk': 2}))
        self.assertEqual(group.membership_set.count(), 1)
        self.assertEqual(group.membership_set.filter(user_id=2).count(), 0)

    def test_leave_group_other(self):
        """
        User leaves a group he is not member of
        """
        self.user_login('admin')
        group = Group.objects.get(pk=2)
        self.assertEqual(group.membership_set.count(), 2)
        self.client.get(reverse('groups:member:leave', kwargs={'group_pk': 2}))
        self.assertEqual(group.membership_set.count(), 2)
        self.assertEqual(group.membership_set.filter(user_id=1).count(), 0)

    def test_kick_out_admin_user(self):
        """
        Admin kicks out regular user
        """
        self.user_login('admin')
        group = Group.objects.get(pk=1)
        self.assertEqual(group.membership_set.count(), 3)
        self.client.get(reverse('groups:member:leave', kwargs={'group_pk': 1, 'user_pk': 2}))
        self.assertEqual(group.membership_set.count(), 2)
        self.assertEqual(group.membership_set.filter(user_id=2).count(), 0)

    def test_kick_out_user_user(self):
        """
        User kicks out regular user
        """
        self.user_login('demo')
        group = Group.objects.get(pk=1)
        self.assertEqual(group.membership_set.count(), 3)
        self.client.get(reverse('groups:member:leave', kwargs={'group_pk': 1, 'user_pk': 2}))
        self.assertEqual(group.membership_set.count(), 3)
        self.assertEqual(group.membership_set.filter(user_id=2).count(), 1)

    def test_kick_out_admin_user_other(self):
        """
        Admin kicks out regular user of different group
        """
        self.user_login('admin')
        group = Group.objects.get(pk=2)
        self.assertEqual(group.membership_set.count(), 2)
        self.client.get(reverse('groups:member:leave', kwargs={'group_pk': 2, 'user_pk': 2}))
        self.assertEqual(group.membership_set.count(), 2)
        self.assertEqual(group.membership_set.filter(user_id=2).count(), 1)

    def test_kick_out_user_user_other(self):
        """
        User kicks out regular user of different group
        """
        self.user_login('test')
        group = Group.objects.get(pk=3)
        self.assertEqual(group.membership_set.count(), 4)
        self.client.get(reverse('groups:member:leave', kwargs={'group_pk': 2, 'user_pk': 15}))
        self.assertEqual(group.membership_set.count(), 4)
        self.assertEqual(group.membership_set.filter(user_id=14).count(), 1)


class GroupAdminTestCase(WgerTestCase):
    """
    Tests promoting and demoting administrators of a group
    """

    def test_promote_admin_member(self):
        """
        Promoter is admin, new user is member
        """
        self.user_login('admin')
        group = Group.objects.get(pk=1)
        self.assertFalse(group.membership_set.get(user_id=2).admin)
        self.client.get(reverse('groups:member:promote', kwargs={'group_pk': 1, 'user_pk': 2}))
        self.assertTrue(group.membership_set.get(user_id=2).admin)

    def test_promote_admin_member_other(self):
        """
        Promoter is admin, new user is member of other group
        """
        self.user_login('admin')
        group = Group.objects.get(pk=1)
        self.assertFalse(group.membership_set.filter(user_id=4).count())
        self.client.get(reverse('groups:member:promote', kwargs={'group_pk': 1, 'user_pk': 4}))
        self.assertFalse(group.membership_set.filter(user_id=4).count())

    def test_promote_member_member(self):
        """
        Promoter is regular member, new user is member of group
        """
        self.user_login('test')
        group = Group.objects.get(pk=1)
        self.assertFalse(group.membership_set.get(user_id=3).admin)
        self.client.get(reverse('groups:member:promote', kwargs={'group_pk': 1,
                                                                 'user_pk': 3}))
        self.assertFalse(group.membership_set.get(user_id=3).admin)

    def test_promote_member_member_other(self):
        """
        Promoter is regular member, new user is member of other group
        """
        self.user_login('test')
        group = Group.objects.get(pk=1)
        self.assertFalse(group.membership_set.filter(user_id=4).count())
        self.client.get(reverse('groups:member:promote', kwargs={'group_pk': 1,
                                                                 'user_pk': 4}))
        self.assertFalse(group.membership_set.filter(user_id=4).count())

    def test_demote_admin_member(self):
        """
        Demoter is admin, other user is member
        """
        self.user_login('admin')
        group = Group.objects.get(pk=1)
        self.assertFalse(group.membership_set.get(user_id=2).admin)
        self.client.get(reverse('groups:member:demote', kwargs={'group_pk': 1,
                                                                'user_pk': 2}))
        self.assertFalse(group.membership_set.get(user_id=2).admin)

    def test_demote_admin_member_other(self):
        """
        Demoter is admin, other user is member of other group
        """
        self.user_login('admin')
        group = Group.objects.get(pk=1)
        self.assertFalse(group.membership_set.filter(user_id=4).count())
        self.client.get(reverse('groups:member:promote', kwargs={'group_pk': 1,
                                                                 'user_pk': 4}))
        self.assertFalse(group.membership_set.filter(user_id=4).count())

    def test_demote_member_admin(self):
        """
        Demoter is regular member, other user is admin
        """
        self.user_login('test')
        group = Group.objects.get(pk=1)
        self.assertTrue(group.membership_set.get(user_id=1).admin)
        self.client.get(reverse('groups:member:demote', kwargs={'group_pk': 1,
                                                                'user_pk': 1}))
        self.assertTrue(group.membership_set.get(user_id=1).admin)

    def test_demote_member_member_other(self):
        """
        Promoter is regular member, new user is member of other group
        """
        self.user_login('test')
        group = Group.objects.get(pk=1)
        self.assertFalse(group.membership_set.filter(user_id=4).count())
        self.client.get(reverse('groups:member:demote', kwargs={'group_pk': 1,
                                                                'user_pk': 4}))
        self.assertFalse(group.membership_set.filter(user_id=4).count())
