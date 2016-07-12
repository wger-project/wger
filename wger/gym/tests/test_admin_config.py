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

from wger.gym.models import GymAdminConfig


class EditConfigTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing an admin config
    '''

    object_class = GymAdminConfig
    url = 'gym:admin_config:edit'
    pk = 1
    user_success = 'admin'
    user_fail = ('member1',
                 'manager1',
                 'manager2',
                 'trainer4',
                 'general_manager1',
                 'general_manager2')
    data = {'overview_inactive': False}
