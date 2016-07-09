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

from django.core.urlresolvers import reverse

from wger.core.tests.base_testcase import WorkoutManagerAccessTestCase, delete_testcase_add_methods
from wger.core.tests.base_testcase import WorkoutManagerAddTestCase
from wger.core.tests.base_testcase import WorkoutManagerDeleteTestCase
from wger.core.tests.base_testcase import WorkoutManagerEditTestCase
from wger.gym.models import UserDocument


class UserDocumentOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing the user document overview page
    '''
    url = reverse('gym:document:list', kwargs={'user_pk': 14})
    anonymous_fail = True
    user_success = ('trainer1',
                    'trainer2',
                    'trainer3')
    user_fail = ('admin',
                 'member1',
                 'member2',
                 'trainer4',
                 'manager3',
                 'general_manager1')


class AddDocumentTestCase(WorkoutManagerAddTestCase):
    '''
    Tests uploading a new user document
    '''

    object_class = UserDocument
    url = reverse('gym:document:add', kwargs={'user_pk': 14})
    fileupload = ['document', 'wger/gym/tests/Wurzelpetersilie.pdf']
    data = {'name': 'Petersilie'}
    data_ignore = ['document']
    user_success = ('trainer1',
                    'trainer2',
                    'trainer3')
    user_fail = ('member1',
                 'member2',
                 'trainer4',
                 'manager3',
                 'general_manager1')


class EditDocumentTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a user document
    '''

    pk = 2
    object_class = UserDocument
    url = 'gym:document:edit'
    data = {'name': 'Petersilie'}
    user_success = ('trainer1',
                    'trainer2',
                    'trainer3')
    user_fail = ('member1',
                 'member2',
                 'trainer4',
                 'manager3',
                 'general_manager1')


class DeleteDocumentTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a user document
    '''

    pk = 1
    object_class = UserDocument
    url = 'gym:document:delete'
    user_success = ('admin',
                    'trainer1',
                    'trainer2',
                    'trainer3')
    user_fail = ('member1',
                 'member2',
                 'trainer4',
                 'manager3',
                 'general_manager1')

delete_testcase_add_methods(DeleteDocumentTestCase)
