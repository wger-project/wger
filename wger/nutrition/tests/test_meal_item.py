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

from wger.nutrition.models import MealItem

from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import ApiBaseResourceTestCase


class EditMealItemUnitTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a meal, set the amount using a unit
    '''

    object_class = MealItem
    url = 'mealitem-edit'
    pk = 4
    data = {'amount': 1,
            'ingredient': 1,
            'weight_unit': 1}


class EditMealItemWeightTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a meal, set the amount using weight
    '''

    object_class = MealItem
    url = 'mealitem-edit'
    pk = 4
    data = {'amount': 100,
            'ingredient': 1}


class AddMealItemUnitTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a meal, set the amount using a unit
    '''

    object_class = MealItem
    url = reverse('mealitem-add', kwargs={'meal_id': 3})
    pk = 22
    data = {'amount': 1,
            'ingredient': 1,
            'weight_unit': 1}


class AddMealItemWeightTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a meal, set the amount using weight
    '''

    object_class = MealItem
    url = reverse('mealitem-add', kwargs={'meal_id': 3})
    pk = 22
    data = {'amount': 100,
            'ingredient': 1}


class MealItemApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests the meal overview resource
    '''
    resource = 'mealitem'
    resource_updatable = False


class MealItemDetailApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests accessing a specific meal
    '''
    resource = 'mealitem/10'
