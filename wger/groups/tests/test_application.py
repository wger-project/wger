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
        count_before = group.application_set.count()

        response = self.client.get(reverse('groups:application:apply',
                                           kwargs={'group_pk': group_pk}))
        count_after = group.application_set.count()
        self.assertEqual(response.status_code, 302)
        if fail:
            self.assertEqual(count_before, count_after)
        else:
            self.assertEqual(count_before + 1, count_after)

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
