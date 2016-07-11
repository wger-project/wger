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
from wger.core.models import UserProfile
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.gym.models import Gym, GymUserConfig


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
                             'g-recaptcha-response': 'PASSED', }
        self.client.post(reverse('core:user:registration'), registration_data)
        new_user = User.objects.all().last()

        self.assertEqual(new_user.userprofile.gym, gym)
        self.assertEqual(new_user.gymuserconfig.gym, gym)

    def test_no_default_gym(self):
        '''
        Test the user registration without a default gym
        '''

        gym_config = GymConfig.objects.get(pk=1)
        gym_config.default_gym = None
        gym_config.save()

        # Register
        registration_data = {'username': 'myusername',
                             'password1': 'secret',
                             'password2': 'secret',
                             'email': 'my.email@example.com',
                             'g-recaptcha-response': 'PASSED', }
        self.client.post(reverse('core:user:registration'), registration_data)

        new_user = User.objects.all().last()
        self.assertEqual(new_user.userprofile.gym_id, None)
        self.assertRaises(GymUserConfig.DoesNotExist, GymUserConfig.objects.get, user=new_user)

    def test_update_userprofile(self):
        '''
        Test setting the gym for users when setting a default gym
        '''

        UserProfile.objects.update(gym=None)
        GymUserConfig.objects.all().delete()
        self.assertEqual(UserProfile.objects.exclude(gym=None).count(), 0)

        gym = Gym.objects.get(pk=2)
        gym_config = GymConfig.objects.get(pk=1)
        gym_config.default_gym = gym
        gym_config.save()

        # 24 users in total
        self.assertEqual(UserProfile.objects.filter(gym=gym).count(), 24)

        # 13 non-managers
        self.assertEqual(GymUserConfig.objects.filter(gym=gym).count(), 13)
