# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

from wger.core.tests.base_testcase import WorkoutManagerEditTestCase

from wger.gym.models import GymUserConfig


class EditConfigTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a user config
    '''

    pk = 1
    object_class = GymUserConfig
    url = 'gym:user_config:edit'
    user_success = 'trainer1'
    user_fail = 'member1'
    user_success = ('trainer1',
                    'trainer2',
                    'trainer3',
                    'admin')
    user_fail = ('general_manager1',
                 'general_manager2',
                 'member1',
                 'member2',
                 'trainer4',
                 'manager3')

    data = {'include_inactive': False}
