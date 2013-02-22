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

from wger.nutrition.models import Meal

from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class EditMealTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a meal
    '''

    object_class = Meal
    url = 'meal-edit'
    pk = 5
    data = {'time': datetime.time(8, 12)}


class AddMealTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a Meal
    '''

    object_class = Meal
    url = reverse('meal-add', kwargs={'plan_pk': 4})
    pk = 12
    data = {'time': datetime.time(9, 2)}
    user_success = 'test'
    user_fail = 'admin'
