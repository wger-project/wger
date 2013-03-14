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

import datetime

from django.core.urlresolvers import reverse

from wger.nutrition.models import MealItem
from wger.nutrition.models import MEALITEM_WEIGHT_UNIT
from wger.nutrition.models import MEALITEM_WEIGHT_GRAM

from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class EditMealItemUnitTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a meal, set the amount using a unit
    '''

    object_class = MealItem
    url = reverse('wger.nutrition.views.ingredient.edit_meal_item',
                  kwargs={'id': 2, 'meal_id': 3, 'item_id': 4})
    pk = 4
    data = {'amount_gramm': 1,
            'ingredient': 1,
            'weight_unit': 1}


class EditMealItemWeightTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a meal, set the amount using weight
    '''

    object_class = MealItem
    url = reverse('wger.nutrition.views.ingredient.edit_meal_item',
                  kwargs={'id': 2, 'meal_id': 3, 'item_id': 4})
    pk = 4
    data = {'amount_gramm': 100,
            'ingredient': 1}


class AddMealItemTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a meal, set the amount using a unit
    '''

    object_class = MealItem
    url = reverse('wger.nutrition.views.ingredient.edit_meal_item',
                  kwargs={'id': 2, 'meal_id': 3, 'item_id': None})
    pk = 22
    data = {'amount_gramm': 1,
            'ingredient': 1,
            'weight_unit': 1}


class AddMealItemTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a meal, set the amount using weight
    '''

    object_class = MealItem
    url = reverse('wger.nutrition.views.ingredient.edit_meal_item',
                  kwargs={'id': 2, 'meal_id': 3, 'item_id': None})
    pk = 22
    data = {'amount_gramm': 100,
            'ingredient': 1}
