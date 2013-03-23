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

from django.core.urlresolvers import reverse

from wger.nutrition.models import Ingredient
from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.workout_manager.constants import PAGINATION_OBJECTS_PER_PAGE


class OverviewPlanTestCase(WorkoutManagerTestCase):
    '''
    Tests the ingredient overview
    '''

    def test_overview(self):

        # Add more ingredients so we can test the pagination
        self.user_login('admin')
        data = {
            "name": "Test ingredient",
            "language": 2,
            "sodium": 10.54,
            "energy": 176,
            "fat": 8.19,
            "carbohydrates_sugar": 0.0,
            "fat_saturated": 3.24,
            "fibres": 0.0,
            "protein": 25.63,
            "carbohydrates": 0.0
        }
        for i in range(0, 50):
            self.client.post(reverse('ingredient-add'), data)

        # Page exists
        self.user_logout()
        response = self.client.get(reverse('ingredient-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ingredients_list']), PAGINATION_OBJECTS_PER_PAGE)

        response = self.client.get(reverse('ingredient-list'),
                                   {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ingredients_list']), PAGINATION_OBJECTS_PER_PAGE)

        rest_ingredients = Ingredient.objects.count() - 2 * PAGINATION_OBJECTS_PER_PAGE
        response = self.client.get(reverse('ingredient-list'),
                                   {'page': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ingredients_list']), rest_ingredients)

        # 'last' is a special case
        response = self.client.get(reverse('ingredient-list'), {'page': 'last'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ingredients_list']), rest_ingredients)

        # Page does not exist
        response = self.client.get(reverse('ingredient-list'), {'page': 100})
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('ingredient-list'), {'page': 'foobar'})
        self.assertEqual(response.status_code, 404)
