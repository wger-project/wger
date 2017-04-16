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
from django.core.urlresolvers import reverse_lazy

from wger.core.models import UserProfile
from wger.core.tests.base_testcase import WorkoutManagerAccessTestCase
from wger.core.tests.base_testcase import WorkoutManagerAddTestCase
from wger.core.tests.base_testcase import WorkoutManagerDeleteTestCase
from wger.core.tests.base_testcase import WorkoutManagerEditTestCase
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.core.tests.base_testcase import delete_testcase_add_methods
from wger.gym.models import Gym


class GymRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(Gym.objects.get(pk=1)), 'Test 123')


class GymOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing the gym overview page
    '''
    url = 'gym:gym:list'
    anonymous_fail = True
    user_success = ('admin',
                    'general_manager1',
                    'general_manager2')
    user_fail = ('member1',
                 'member2',
                 'trainer2',
                 'trainer3',
                 'trainer4',
                 'manager3')


class GymUserOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing the gym user overview page
    '''
    url = reverse_lazy('gym:gym:user-list', kwargs={'pk': 1})
    anonymous_fail = True
    user_success = ('admin',
                    'trainer2',
                    'trainer3',
                    'manager1',
                    'general_manager1',
                    'general_manager2')
    user_fail = ('member1',
                 'member2',
                 'trainer4',
                 'manager3')


class AddGymTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new gym
    '''
    object_class = Gym
    url = 'gym:gym:add'
    data = {'name': 'The name here'}
    user_success = ('admin',
                    'general_manager1')
    user_fail = ('member1',
                 'member2',
                 'trainer2',
                 'trainer3',
                 'trainer4',
                 'manager1',
                 'manager3')


class DeleteGymTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a gym
    '''

    pk = 2
    object_class = Gym
    url = 'gym:gym:delete'
    user_success = ('admin',
                    'general_manager1',
                    'general_manager2')
    user_fail = ('member1',
                 'member2',
                 'trainer2',
                 'trainer3',
                 'trainer4',
                 'manager1',
                 'manager3')


delete_testcase_add_methods(DeleteGymTestCase)


class EditGymTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a gym
    '''

    object_class = Gym
    url = 'gym:gym:edit'
    pk = 1
    data = {'name': 'A different name'}
    user_success = ('admin',
                    'manager1',
                    'general_manager1',
                    'general_manager2')
    user_fail = ('member1',
                 'member2',
                 'trainer2',
                 'trainer3',
                 'trainer4',
                 'manager3')


class GymTestCase(WorkoutManagerTestCase):
    '''
    Tests other gym methods
    '''

    def test_delete_gym(self):
        '''
        Tests that deleting a gym also removes it from all user profiles
        '''
        gym = Gym.objects.get(pk=1)
        self.assertEqual(UserProfile.objects.filter(gym=gym).count(), 17)

        gym.delete()
        self.assertEqual(UserProfile.objects.filter(gym=gym).count(), 0)
