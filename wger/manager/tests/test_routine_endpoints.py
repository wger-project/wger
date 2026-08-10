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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Django
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase


URL_NAMES = (
    'routine-date-sequence-display-mode',
    'routine-date-sequence-gym-mode',
    'routine-structure',
)


class RoutineDetailEndpointsApiTestCase(BaseTestCase, ApiBaseTestCase):
    """
    Tests the detail endpoints used by the mobile and web apps

    Routine 1 belongs to admin, has three days and is not public.
    """

    def test_anonymous(self):
        for url_name in URL_NAMES:
            response = self.client.get(reverse(url_name, kwargs={'pk': 1}))
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f'{url_name} did not return 403 for anonymous users',
            )

    def test_other_user(self):
        self.authenticate('test')
        for url_name in URL_NAMES:
            response = self.client.get(reverse(url_name, kwargs={'pk': 1}))
            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
                f'{url_name} leaked a foreign routine',
            )

    def test_date_sequence_display(self):
        self.authenticate('admin')
        response = self.client.get(reverse('routine-date-sequence-display-mode', kwargs={'pk': 1}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data)

        first_day = data[0]
        self.assertIn('iteration', first_day)
        self.assertIn('date', first_day)
        self.assertIn('day', first_day)
        self.assertIn('slots', first_day)

    def test_date_sequence_gym(self):
        self.authenticate('admin')
        response = self.client.get(reverse('routine-date-sequence-gym-mode', kwargs={'pk': 1}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data)
        self.assertIn('day', data[0])

    def test_structure(self):
        self.authenticate('admin')
        response = self.client.get(reverse('routine-structure', kwargs={'pk': 1}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['id'], 1)
        self.assertEqual(len(data['days']), 3)
        self.assertTrue(any(day['slots'] for day in data['days']))
