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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from wger.groups.models import Group, Application
from wger.manager.tests.testcase import WorkoutManagerTestCase


class ApplyGroupTestCase(WorkoutManagerTestCase):
    '''
    Tests the workflow to apply joining a private group
    '''

    def apply_group(self, fail=False, username='', group_pk=2):
        '''
        Helper method to apply to private groups
        '''
        self.user_login(username)

        group = Group.objects.get(pk=group_pk)
        count_applications_before = group.application_set.count()
        count_members_before = group.membership_set.count()
        count_admins_before = group.membership_set.filter(admin=True).count()

        response = self.client.get(reverse('groups:application:apply',
                                           kwargs={'group_pk': group_pk}))
        count_applications_after = group.application_set.count()
        count_members_after = group.membership_set.count()
        count_admins_after = group.membership_set.filter(admin=True).count()
        self.assertEqual(count_admins_before, count_admins_after)
        self.assertEqual(count_members_before, count_members_after)
        self.assertEqual(response.status_code, 302)
        if fail:
            self.assertEqual(count_applications_before, count_applications_after)
        else:
            self.assertEqual(count_applications_before + 1, count_applications_after)

    def test_apply_private_group_no_member(self):
        '''
        Apply to join a private group, without being already a member
        '''
        self.apply_group(fail=False, username='member1', group_pk=2)

    def test_apply_private_group_already_applied(self):
        '''
        Apply to join a private group, while having already having applied
        '''
        application = Application()
        application.user = User.objects.get(username='member1')
        application.group_id = 2
        application.save()
        self.apply_group(fail=True, username='member1', group_pk=2)

    def test_apply_private_group_member(self):
        '''
        Apply to join a private group, while being already a member
        '''
        self.apply_group(fail=True, username='trainer1', group_pk=2)

    def test_apply_public_group_no_member(self):
        '''
        Apply to join a public group, without being already a member
        '''
        self.apply_group(fail=True, username='member1', group_pk=1)

    def test_apply_public_group_member(self):
        '''
        Apply to join a public group, while being already a member
        '''
        self.apply_group(fail=True, username='test', group_pk=1)


class AcceptApplicationTestCase(WorkoutManagerTestCase):
    '''
    Tests the workflow to accept an application to join a private group
    '''

    def accept_application(self, fail=False):
        '''
        Helper method to accept applications
        '''
        group_pk = 2

        group = Group.objects.get(pk=group_pk)
        count_applications_before = group.application_set.count()
        count_members_before = group.membership_set.count()
        count_admins_before = group.membership_set.filter(admin=True).count()
        response = self.client.get(reverse('groups:application:accept',
                                           kwargs={'group_pk': group_pk,
                                                   'user_pk': 17}))
        count_applications_after = group.application_set.count()
        count_members_after = group.membership_set.count()
        count_admins_after = group.membership_set.filter(admin=True).count()
        self.assertEqual(count_admins_before, count_admins_after)
        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertEqual(count_members_before, count_members_after)
            self.assertEqual(count_applications_before, count_applications_after)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_members_before + 1, count_members_after)
            self.assertEqual(count_applications_before - 1, count_applications_after)

    def test_accept_application_admin_own_group(self):
        '''
        Accept application to join own private group, being admin
        '''
        self.user_login('test')
        self.accept_application(fail=False)

    def test_accept_application_twice(self):
        '''
        Accept application to join own private group twice
        '''
        self.user_login('test')
        self.accept_application(fail=False)
        self.accept_application(fail=True)

    def test_accept_application_not_admin_own_group(self):
        '''
        Accept application to join own private group, being admin
        '''
        self.user_login('trainer1')
        self.accept_application(fail=True)

    def test_accept_application_admin_other_group(self):
        '''
        Accept application to join private group, being admin in other group
        '''
        self.user_login('admin')
        self.accept_application(fail=True)

    def test_accept_application_not_admin_other_group(self):
        '''
        Accept application to join private group, being regular user in other group
        '''
        self.user_login('member2')
        self.accept_application(fail=True)

    def test_accept_application_anonymous(self):
        '''
        Accept application to join private group as an anonymous user
        '''
        self.accept_application(fail=True)


class DenyApplicationTestCase(WorkoutManagerTestCase):
    '''
    Tests the workflow to deny an application to join a private group
    '''

    def deny_application(self, fail=False):
        '''
        Helper method to deny applications
        '''
        group_pk = 2

        group = Group.objects.get(pk=group_pk)
        count_applications_before = group.application_set.count()
        count_members_before = group.membership_set.count()
        count_admins_before = group.membership_set.filter(admin=True).count()
        response = self.client.get(reverse('groups:application:deny',
                                           kwargs={'group_pk': group_pk,
                                                   'user_pk': 17}))
        count_applications_after = group.application_set.count()
        count_members_after = group.membership_set.count()
        count_admins_after = group.membership_set.filter(admin=True).count()
        self.assertEqual(count_members_before, count_members_after)
        self.assertEqual(count_admins_before, count_admins_after)
        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertEqual(count_applications_before, count_applications_after)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_applications_before - 1, count_applications_after)

    def test_deny_application_admin_own_group(self):
        '''
        Deny application to join own private group, being admin
        '''
        self.user_login('test')
        self.deny_application(fail=False)

    def test_deny_application_twice(self):
        '''
        Deny application to join own private group twice
        '''
        self.user_login('test')
        self.deny_application(fail=False)
        self.deny_application(fail=True)

    def test_deny_application_not_admin_own_group(self):
        '''
        Deny application to join own private group, being admin
        '''
        self.user_login('trainer1')
        self.deny_application(fail=True)

    def test_deny_application_admin_other_group(self):
        '''
        Deny application to join private group, being admin in other group
        '''
        self.user_login('admin')
        self.deny_application(fail=True)

    def test_deny_application_not_admin_other_group(self):
        '''
        Deny application to join private group, being regular user in other group
        '''
        self.user_login('member2')
        self.deny_application(fail=True)

    def test_deny_application_anonymous(self):
        '''
        Deny application to join private group as an anonymous user
        '''
        self.deny_application(fail=True)
