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

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE


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
            "carbohydrates": 0.0,
            'license': 1,
            'license_author': 'internet'
        }
        for i in range(0, 50):
            self.client.post(reverse('nutrition:ingredient:add'), data)

        # Page exists
        self.user_logout()
        response = self.client.get(reverse('nutrition:ingredient:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ingredients_list']), PAGINATION_OBJECTS_PER_PAGE)

        response = self.client.get(reverse('nutrition:ingredient:list'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ingredients_list']), PAGINATION_OBJECTS_PER_PAGE)

        rest_ingredients = 13
        response = self.client.get(reverse('nutrition:ingredient:list'), {'page': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ingredients_list']), rest_ingredients)

        # 'last' is a special case
        response = self.client.get(reverse('nutrition:ingredient:list'), {'page': 'last'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ingredients_list']), rest_ingredients)

        # Page does not exist
        response = self.client.get(reverse('nutrition:ingredient:list'), {'page': 100})
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('nutrition:ingredient:list'), {'page': 'foobar'})
        self.assertEqual(response.status_code, 404)

    def ingredient_overview(self, logged_in=True, demo=False, admin=False):
        '''
        Helper function to test the ingredient overview page
        '''

        # Page exists
        response = self.client.get(reverse('nutrition:ingredient:list'))
        self.assertEqual(response.status_code, 200)

        # No ingredients pending review
        if admin:
            self.assertContains(response, 'Ingredients pending review')
        else:
            self.assertNotContains(response, 'Ingredients pending review')

        # Only authorized users see the edit links
        if logged_in and not demo:
            self.assertNotContains(response, 'Only registered users can do this')

        if logged_in and demo:
            self.assertContains(response, 'Only registered users can do this')

    def test_ingredient_index_editor(self):
        '''
        Tests the ingredient overview page as a logged in user with editor rights
        '''

        self.user_login('admin')
        self.ingredient_overview(admin=True)

    def test_ingredient_index_non_editor(self):
        '''
        Tests the overview overview page as a logged in user without editor rights
        '''

        self.user_login('test')
        self.ingredient_overview()

    def test_ingredient_index_demo_user(self):
        '''
        Tests the overview overview page as a logged in demo user
        '''

        self.user_login('demo')
        self.ingredient_overview(demo=True)

    def test_ingredient_index_logged_out(self):
        '''
        Tests the overview overview page as an anonymous (logged out) user
        '''

        self.ingredient_overview(logged_in=False)
