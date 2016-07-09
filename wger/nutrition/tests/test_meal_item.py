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

from django.core.urlresolvers import reverse

from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WorkoutManagerAddTestCase
from wger.core.tests.base_testcase import WorkoutManagerEditTestCase
from wger.nutrition.models import MealItem


class EditMealItemUnitTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a meal, set the amount using a unit
    '''

    object_class = MealItem
    url = 'nutrition:meal_item:edit'
    pk = 4
    data = {'amount': 1,
            'ingredient': 1,
            'weight_unit': 1}


class EditMealItemWeightTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a meal, set the amount using weight
    '''

    object_class = MealItem
    url = 'nutrition:meal_item:edit'
    pk = 4
    data = {'amount': 100,
            'ingredient': 1}


class AddMealItemUnitTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a meal, set the amount using a unit
    '''

    object_class = MealItem
    url = reverse('nutrition:meal_item:add', kwargs={'meal_id': 3})
    data = {'amount': 1,
            'ingredient': 1,
            'weight_unit': 1}


class AddMealItemWeightTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a meal, set the amount using weight
    '''

    object_class = MealItem
    url = reverse('nutrition:meal_item:add', kwargs={'meal_id': 3})
    data = {'amount': 100,
            'ingredient': 1}


class MealItemApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the meal overview resource
    '''
    pk = 10
    resource = MealItem
    private_resource = True
    special_endpoints = ('nutritional_values',)
    data = {'meal': 2,
            'amount': 100,
            'ingredient': 1}
