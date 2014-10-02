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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from wger.config.models import GymConfig
from wger.core.models import Gym, UserProfile
from wger.manager.tests.testcase import WorkoutManagerTestCase


class GymConfigTestCase(WorkoutManagerTestCase):
    '''
    Test the system wide gym configuration
    '''

    def test_default_gym(self):
        '''
        Test that newly registered users get a gym
        '''

        gym = Gym.objects.get(pk=2)
        gym_config = GymConfig.objects.get(pk=1)
        gym_config.default_gym = gym
        gym_config.save()

        # Register
        registration_data = {'username': 'myusername',
                             'password1': 'secret',
                             'password2': 'secret',
                             'email': 'my.email@example.com',
                             'recaptcha_response_field': 'PASSED', }
        self.client.post(reverse('core:registration'), registration_data)
        new_user = User.objects.get(pk=14)

        self.assertEqual(new_user.userprofile.gym, gym)

    def test_no_default_gym(self):
        '''
        Test the user registration without a default gym
        '''

        gym = Gym.objects.get(pk=2)
        gym_config = GymConfig.objects.get(pk=1)
        gym_config.default_gym = None
        gym_config.save()

        # Register
        registration_data = {'username': 'myusername',
                             'password1': 'secret',
                             'password2': 'secret',
                             'email': 'my.email@example.com',
                             'recaptcha_response_field': 'PASSED', }
        self.client.post(reverse('core:registration'), registration_data)

        new_user = User.objects.get(pk=14)
        self.assertEqual(new_user.userprofile.gym_id, None)

    def test_update_userprofile(self):
        '''
        Test setting the gym for users when setting a default gym
        '''

        UserProfile.objects.update(gym=None)
        self.assertEqual(UserProfile.objects.exclude(gym=None).count(), 0)

        gym = Gym.objects.get(pk=2)
        gym_config = GymConfig.objects.get(pk=1)
        gym_config.default_gym = gym
        gym_config.save()

        self.assertEqual(UserProfile.objects.filter(gym=gym).count(), 13)
