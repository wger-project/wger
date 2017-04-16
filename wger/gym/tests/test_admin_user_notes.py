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

from wger.core.tests.base_testcase import WorkoutManagerAccessTestCase
from wger.core.tests.base_testcase import WorkoutManagerAddTestCase
from wger.core.tests.base_testcase import WorkoutManagerDeleteTestCase
from wger.core.tests.base_testcase import WorkoutManagerEditTestCase
from wger.core.tests.base_testcase import delete_testcase_add_methods
from wger.gym.models import AdminUserNote


class AdminNoteOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing the admin notes overview page
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
    Tests adding a new admin note
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
    Tests editing an admin note
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
    Tests deleting an admin note
    '''

    pk = 2
    object_class = AdminUserNote
    url = 'gym:admin_note:delete'
    user_success = ('trainer1',
                    'trainer2',
                    'trainer3')
    user_fail = ('member1',
                 'manager1',
                 'manager2',
                 'trainer4',
                 'general_manager1',
                 'general_manager2')


delete_testcase_add_methods(DeleteAdminNoteTestCase)
