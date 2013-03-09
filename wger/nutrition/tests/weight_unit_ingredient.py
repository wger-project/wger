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

from django.core.urlresolvers import reverse_lazy

from wger.nutrition.models import IngredientWeightUnit

from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class AddWeightUnitIngredientTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new weight unit to an ingredient
    '''

    object_class = IngredientWeightUnit
    url = reverse_lazy('weight-unit-ingredient-add',
                       kwargs={'ingredient_pk': 1})
    data = {'unit': 1,
            'gramm': 123,
            'amount': 1}
    pk = 4


class DeleteWeightUnitIngredientTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a weight unit from an ingredient
    '''

    object_class = IngredientWeightUnit
    url = 'weight-unit-ingredient-delete'
    pk = 1


class EditWeightUnitTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a weight unit from an ingredient
    '''

    object_class = IngredientWeightUnit
    url = 'weight-unit-ingredient-edit'
    pk = 1
    data = {'unit': 1,
            'gramm': 10,
            'amount': 0.3}
