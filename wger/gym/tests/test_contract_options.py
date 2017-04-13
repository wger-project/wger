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

from wger.core.tests.base_testcase import (
    WorkoutManagerEditTestCase,
    WorkoutManagerAddTestCase,
    WorkoutManagerDeleteTestCase,
    WorkoutManagerAccessTestCase,
    delete_testcase_add_methods)
from wger.gym.models import ContractOption


class AddContractOptionTestCase(WorkoutManagerAddTestCase):
    '''
    Tests creating a new contract option
    '''

    object_class = ContractOption
    url = reverse('gym:contract-option:add', kwargs={'gym_pk': 1})
    data = {'name': 'Some name'}
    user_success = ('manager1',
                    'manager2')
    user_fail = ('admin',
                 'general_manager1',
                 'manager3',
                 'manager4',
                 'test',
                 'member1',
                 'member2',
                 'member3',
                 'member4',
                 'member5')


class EditContractOptionTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a contract option
    '''

    pk = 1
    object_class = ContractOption
    url = 'gym:contract-option:edit'
    user_success = ('manager1',
                    'manager2')
    user_fail = ('admin',
                 'general_manager1',
                 'manager3',
                 'manager4',
                 'test',
                 'member1',
                 'member2',
                 'member3',
                 'member4',
                 'member5')
    data = {'name': 'Standard contract 16-Gj'}


class DeleteContractOptionTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a contract option
    '''

    pk = 1
    object_class = ContractOption
    url = 'gym:contract-option:delete'
    user_success = ('manager1',
                    'manager2')
    user_fail = ('admin',
                 'general_manager1',
                 'manager3',
                 'manager4',
                 'test',
                 'member1',
                 'member2',
                 'member3',
                 'member4',
                 'member5')


delete_testcase_add_methods(DeleteContractOptionTestCase)


class AccessContractOptionOverviewTestCase(WorkoutManagerAccessTestCase):
    '''
    Test accessing the contract option page
    '''
    url = reverse('gym:contract-option:list', kwargs={'gym_pk': 1})
    user_success = ('manager1',
                    'manager2')
    user_fail = ('admin',
                 'general_manager1',
                 'manager3',
                 'manager4',
                 'test',
                 'member1',
                 'member2',
                 'member3',
                 'member4',
                 'member5')
