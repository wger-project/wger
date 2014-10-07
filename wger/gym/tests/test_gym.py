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
from django.core.urlresolvers import reverse_lazy

from wger.core.models import UserProfile
from wger.gym.models import Gym

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerAccessTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class GymOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing the gym overview page
    '''
    url = 'gym:gym:list'
    anonymous_fail = True


class GymUserOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing the gym user overview page
    '''
    url = reverse_lazy('gym:gym:user-list', kwargs={'pk': 1})
    anonymous_fail = True


class AddGymTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new gym
    '''
    object_class = Gym
    url = 'gym:gym:add'
    data = {'name': 'The name here'}
    pk = 4


class DeleteGymTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a gym
    '''

    object_class = Gym
    url = 'gym:gym:delete'
    pk = 2


class EditGymTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a license
    '''

    object_class = Gym
    url = 'gym:gym:edit'
    pk = 1
    data = {'name': 'A different name'}


class GymTestCase(WorkoutManagerTestCase):
    '''
    Tests other methods
    '''

    def test_delete_gym(self):
        '''
        Tests that deleting a gym also removes it from all user profiles
        '''
        gym = Gym.objects.get(pk=1)
        self.assertEqual(UserProfile.objects.filter(gym=gym).count(), 8)

        gym.delete()
        self.assertEqual(UserProfile.objects.filter(gym=gym).count(), 0)
