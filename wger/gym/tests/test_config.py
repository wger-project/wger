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

# wger
from wger.core.tests.base_testcase import (
    WgerEditTestCase,
    WgerTestCase,
)
from wger.gym.models import GymConfig


class EditGymConfigTestCase(WgerEditTestCase):
    """
    Test editing a gym configuration
    """

    pk = 1
    object_class = GymConfig
    url = 'gym:config:edit'
    data = {'weeks_inactive': 10, 'show_name': True}
    user_success = (
        'admin',
        'manager1',
        'manager2',
    )
    user_fail = (
        'member1',
        'general_manager1',
        'trainer1',
        'trainer2',
        'trainer3',
        'trainer4',
        'manager3',
    )


class EditGymConfigOwnershipTestCase(WgerTestCase):
    """
    Managers can only edit the config of their own gym, also when the ids of the
    config and the gym differ (config 2 belongs to gym 3 in the fixtures)
    """

    data = {'weeks_inactive': 99, 'show_name': True}

    def edit(self, config_pk: int) -> int:
        self.user_login('manager3')  # gym 2
        response = self.client.post(reverse('gym:config:edit', kwargs={'pk': config_pk}), self.data)
        return response.status_code

    def test_config_of_other_gym(self):
        self.assertEqual(GymConfig.objects.get(pk=2).gym_id, 3)

        self.assertEqual(self.edit(2), 403)
        self.assertNotEqual(GymConfig.objects.get(pk=2).weeks_inactive, 99)

    def test_config_of_own_gym(self):
        self.assertEqual(GymConfig.objects.get(pk=3).gym_id, 2)

        self.assertEqual(self.edit(3), 302)
        self.assertEqual(GymConfig.objects.get(pk=3).weeks_inactive, 99)
