# -*- coding: utf-8 -*-

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
from wger.core.tests.base_testcase import WgerTestCase
from wger.gym.models import Gym


class GymNameHeaderTestCase(WgerTestCase):
    """
    Test case for showing gym name on application header
    """

    def check_header(self, gym=None):
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.context['custom_header'], gym)

    def test_custom_header_gym_members(self):
        """
        Test the custom header for gym members
        """

        # Gym 1, custom header activated
        gym = Gym.objects.get(pk=1)
        self.assertTrue(gym.config.show_name)
        for username in (
            'test',
            'member1',
            'member2',
            'member3',
            'member4',
            'member5',
        ):
            self.user_login(username)
            self.check_header(gym=gym.name)

        # Gym 2, custom header deactivated
        gym = Gym.objects.get(pk=2)
        self.assertFalse(gym.config.show_name)
        for username in (
            'trainer4',
            'trainer5',
            'demo',
            'member6',
            'member7',
        ):
            self.user_login(username)
            self.check_header(gym=None)

    def test_custom_header_anonymous_user(self):
        """
        Test the custom header for logged out users
        """
        self.check_header(gym=None)
