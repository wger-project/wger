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
from wger.gym.models import ContractType


class AddContractTypeTestCase(WorkoutManagerAddTestCase):
    '''
    Tests creating a new contract
    '''

    object_class = ContractType
    url = reverse('gym:contract_type:add', kwargs={'gym_pk': 1})
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


class EditContractTypeTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a contract type
    '''

    pk = 1
    object_class = ContractType
    url = 'gym:contract_type:edit'
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


class DeleteContractTypeTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a contract type
    '''

    pk = 1
    object_class = ContractType
    url = 'gym:contract_type:delete'
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


delete_testcase_add_methods(DeleteContractTypeTestCase)


class AccessContractTypeOverviewTestCase(WorkoutManagerAccessTestCase):
    '''
    Test accessing the contract list page
    '''
    url = reverse('gym:contract_type:list', kwargs={'gym_pk': 1})
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
