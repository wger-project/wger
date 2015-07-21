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
from django.core.urlresolvers import reverse_lazy

from wger.groups.models import Group
from wger.manager.tests.testcase import WorkoutManagerTestCase, WorkoutManagerAccessTestCase


class GroupRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(Group.objects.get(pk=1)), 'Cool team')


class PublicGroupDetailAccessTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing a detail view of a public group
    '''
    url = reverse_lazy('groups:group:view', kwargs={'pk': 1})
    anonymous_fail = True
    user_success = ('admin',
                    'test',
                    'demo',
                    'trainer1',
                    'trainer2',
                    'trainer3',
                    'manager1',
                    'general_manager1',
                    'general_manager2')
    user_fail = ()


class PrivateGroupDetailAccessTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing a detail view of a private group
    '''
    url = reverse_lazy('groups:group:view', kwargs={'pk': 2})
    anonymous_fail = True
    user_success = ('test',)
    user_fail = ('admin',
                 'demo',
                 'trainer1')


class GroupOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing the group overview page
    '''
    url = reverse_lazy('groups:group:list')
    anonymous_fail = True
    user_success = ('admin',
                    'test',
                    'demo',
                    'trainer1',
                    'trainer2',
                    'trainer3',
                    'manager1',
                    'general_manager1',
                    'general_manager2')
    user_fail = ()
