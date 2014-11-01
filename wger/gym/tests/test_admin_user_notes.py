# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

from django.core.urlresolvers import reverse_lazy

from wger.manager.tests.testcase import WorkoutManagerAccessTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase

from wger.gym.models import AdminUserNote


class AdminNoteOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing the gym overview page
    '''
    url = reverse_lazy('gym:admin_note:list', kwargs={'user_pk': 14})
    anonymous_fail = True
    user_success = ('trainer1',
                    'trainer2',
                    'trainer3')
    user_fail = ('member1',
                 'manager1',
                 'manager2',
                 'trainer4',
                 'general_manager1',
                 'general_manager2')


class AddAdminNoteTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new gym
    '''
    object_class = AdminUserNote
    url = reverse_lazy('gym:admin_note:add', kwargs={'user_pk': 14})
    data = {'note': 'The note text goes here'}
    user_success = ('trainer1',
                    'trainer2',
                    'trainer3')
    user_fail = ('member1',
                 'manager1',
                 'manager2',
                 'trainer4',
                 'general_manager1',
                 'general_manager2')


class EditAdminNoteTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing an admin config
    '''

    object_class = AdminUserNote
    url = 'gym:admin_note:edit'
    pk = 1
    user_success = ('trainer1',
                    'trainer2',
                    'trainer3')
    user_fail = ('member1',
                 'manager1',
                 'manager2',
                 'trainer4',
                 'general_manager1',
                 'general_manager2')
    data = {'note': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr'}


class DeleteAdminNoteTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a gym
    '''

    pk = 2
    object_class = AdminUserNote
    url = 'gym:admin_note:delete'
    user_success = 'trainer1'
    # user_success = ('trainer1',
    #                'trainer2',
    #                'trainer3')
    user_fail = ('member1',
                 'manager1',
                 'manager2',
                 'trainer4',
                 'general_manager1',
                 'general_manager2')
