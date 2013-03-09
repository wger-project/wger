# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from wger.nutrition.models import WeightUnit

from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class AddWeightUnitTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new weight unit
    '''

    object_class = WeightUnit
    url = 'weight-unit-add'
    data = {'name': 'A new weight unit'}
    pk = 7


class DeleteWeightUnitTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a weight unit
    '''

    object_class = WeightUnit
    url = 'weight-unit-delete'
    pk = 1


class EditWeightUnitTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a weight unit
    '''

    object_class = WeightUnit
    url = 'weight-unit-edit'
    pk = 1
    data = {'name': 'A new name'}
