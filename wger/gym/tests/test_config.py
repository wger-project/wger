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

from wger.core.tests.base_testcase import WorkoutManagerEditTestCase
from wger.gym.models import GymConfig


class EditGymConfigTestCase(WorkoutManagerEditTestCase):
    '''
    Test editing a gym configuration
    '''

    pk = 1
    object_class = GymConfig
    url = 'gym:config:edit'
    data = {'weeks_inactive': 10}
    user_success = ('admin',
                    'manager1',
                    'manager2')
    user_fail = ('member1',
                 'general_manager1',
                 'trainer1',
                 'trainer2',
                 'trainer3',
                 'trainer4',
                 'manager3')
