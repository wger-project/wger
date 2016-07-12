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
    WorkoutManagerAccessTestCase,
    WorkoutManagerEditTestCase,
    WorkoutManagerAddTestCase,
)
from wger.gym.models import Contract


class AddContractTestCase(WorkoutManagerAddTestCase):
    '''
    Tests creating a new contract
    '''

    object_class = Contract
    url = reverse('gym:contract:add', kwargs={'user_pk': 14})
    data = {'amount': 30,
            'payment': '2'}
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


class AccessContractTestCase(WorkoutManagerAccessTestCase):
    '''
    Test accessing the detail page of a contract
    '''
    url = reverse('gym:contract:view', kwargs={'pk': 1})
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


class AccessContractOverviewTestCase(WorkoutManagerAccessTestCase):
    '''
    Test accessing the contract list page
    '''
    url = reverse('gym:contract:list', kwargs={'user_pk': 4})
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


class EditContractTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a contract
    '''

    pk = 1
    object_class = Contract
    url = 'gym:contract:edit'
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
    data = {'note': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr',
            'amount': 35,
            'payment': '5'}
