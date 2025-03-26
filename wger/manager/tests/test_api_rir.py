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
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.base_testcase import WgerTestCase


class RiRApiTestCase(WgerTestCase):
    """
    Test the validators for the RiR entries
    """

    def setUp(self):
        super().setUp()
        self.user_login()

    def test_rir_config_1(self):
        response = self.client.post(
            reverse('rir-config-list'),
            data={
                'iteration': 1,
                'slot_entry': 1,
                'value': 1.4,
                'operation': 'r',
                'step': 'abs',
            },
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            '1.4 is not a valid RiR option',
            data['value'][0],
        )

    def test_rir_config_2(self):
        response = self.client.post(
            reverse('rir-config-list'),
            data={
                'iteration': 1,
                'slot_entry': 1,
                'value': -1,
                'operation': 'r',
                'step': 'abs',
            },
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Ensure this value is either NULL or greater than or equal to 0.',
            data['value'][0],
        )

    def test_max_rir_config1(self):
        response = self.client.post(
            reverse('max-rir-config-list'),
            data={
                'iteration': 1,
                'slot_entry': 1,
                'value': -1.4,
                'operation': 'r',
                'step': 'abs',
            },
        )
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('-1.4 is not a valid RiR option', data['value'][1])
        self.assertIn(
            'Ensure this value is either NULL or greater than or equal to 0.', data['value'][0]
        )

    def test_log_1(self):
        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'iteration': 1,
                'exercise': 1,
                'slot_entry': 1,
                'rir': 1.3,
                'rir_target': 1.6,
            },
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('1.3 is not a valid RiR option', data['rir'][0])
        self.assertIn('1.6 is not a valid RiR option', data['rir_target'][0])
