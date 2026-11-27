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
from wger.core.tests.base_testcase import (
    WgerAccessTestCase,
    WgerAddTestCase,
    WgerEditTestCase,
    WgerTestCase,
)
from wger.gym.models import (
    Contract,
    ContractOption,
    ContractType,
)


class AddContractTestCase(WgerAddTestCase):
    """
    Tests creating a new contract
    """

    object_class = Contract
    url = reverse('gym:contract:add', kwargs={'user_pk': 14})
    data = {'amount': 30, 'payment': '2'}
    user_success = ('manager1', 'manager2')
    user_fail = (
        'admin',
        'general_manager1',
        'manager3',
        'test',
        'member1',
        'member2',
        'member3',
        'member4',
        'member5',
    )


class AccessContractTestCase(WgerAccessTestCase):
    """
    Test accessing the detail page of a contract
    """

    url = reverse('gym:contract:view', kwargs={'pk': 1})
    user_success = ('manager1', 'manager2')
    user_fail = (
        'admin',
        'general_manager1',
        'manager3',
        'test',
        'member1',
        'member2',
        'member3',
        'member4',
        'member5',
    )


class AccessContractOverviewTestCase(WgerAccessTestCase):
    """
    Test accessing the contract list page
    """

    url = reverse('gym:contract:list', kwargs={'user_pk': 4})
    user_success = ('manager1', 'manager2')
    user_fail = (
        'admin',
        'general_manager1',
        'manager3',
        'test',
        'member1',
        'member2',
        'member3',
        'member4',
        'member5',
    )


class EditContractTestCase(WgerEditTestCase):
    """
    Tests editing a contract
    """

    pk = 1
    object_class = Contract
    url = 'gym:contract:edit'
    user_success = ('manager1', 'manager2')
    user_fail = (
        'admin',
        'general_manager1',
        'manager3',
        'test',
        'member1',
        'member2',
        'member3',
        'member4',
        'member5',
    )
    data = {
        'note': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr',
        'amount': 35,
        'payment': '5',
    }


class ContractFormGymScopeTestCase(WgerTestCase):
    """
    Tests that the contract forms only offer and accept types and options of the member's gym
    """

    def setUp(self):
        super().setUp()
        self.member = User.objects.get(username='member6')
        self.other_type = ContractType.objects.get(name='Standard contract 12/b')
        self.other_options = ContractOption.objects.filter(gym_id=self.other_type.gym_id)
        self.own_type = ContractType.objects.create(gym_id=2, name='Gym two contract')
        self.own_option = ContractOption.objects.create(gym_id=2, name='Gym two option')
        self.user_login('manager3')

    def post_data(self, contract_type, options):
        return {
            'contract_type': contract_type.pk,
            'options': [o.pk for o in options],
            'amount': 10,
            'payment': '1',
            'is_active': 'on',
            'date_start': '2026-01-01',
        }

    def test_add_form_lists_only_own_gym(self):
        """The add form lists the own gym's types and options and no others"""
        response = self.client.get(reverse('gym:contract:add', kwargs={'user_pk': self.member.pk}))
        self.assertContains(response, 'Gym two contract')
        self.assertContains(response, 'Gym two option')
        self.assertNotContains(response, 'Standard contract 12/b')
        self.assertNotContains(response, 'Pays cash')

    def test_add_rejects_other_gym(self):
        """Adding a contract with another gym's type or options is rejected"""
        url = reverse('gym:contract:add', kwargs={'user_pk': self.member.pk})
        response = self.client.post(url, self.post_data(self.other_type, [self.own_option]))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, self.post_data(self.own_type, self.other_options))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contract.objects.filter(member=self.member).exists())

    def test_add_accepts_own_gym(self):
        """Adding a contract with the own gym's type and options works"""
        url = reverse('gym:contract:add', kwargs={'user_pk': self.member.pk})
        response = self.client.post(url, self.post_data(self.own_type, [self.own_option]))
        self.assertEqual(response.status_code, 302)
        contract = Contract.objects.get(member=self.member)
        self.assertEqual(contract.contract_type, self.own_type)
        self.assertEqual(list(contract.options.all()), [self.own_option])

    def test_edit_rejects_other_gym(self):
        """Editing a contract cannot bind another gym's type or options"""
        contract = Contract.objects.create(
            member=self.member,
            user=User.objects.get(username='manager3'),
            contract_type=self.own_type,
            amount=10,
            payment='1',
        )
        url = reverse('gym:contract:edit', kwargs={'pk': contract.pk})

        response = self.client.get(url)
        self.assertContains(response, 'Gym two contract')
        self.assertNotContains(response, 'Standard contract 12/b')
        self.assertNotContains(response, 'Pays cash')

        self.client.post(url, self.post_data(self.other_type, self.other_options))
        contract.refresh_from_db()
        self.assertEqual(contract.contract_type, self.own_type)
        self.assertFalse(contract.options.exists())
