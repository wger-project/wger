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

from wger.workout_manager.constants import NUTRITION_TAB

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class DeleteIngredientTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting an ingredient
    '''

    object_class = Ingredient
    url = 'ingredient-delete'
    pk = 1


class EditIngredientTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing an ingredient
    '''

    object_class = Ingredient
    url = 'ingredient-edit'
    pk = 1
    data = {'name': 'A new name',
            'sodium': 2,
            'energy': 200,
            'fat': 10,
            'carbohydrates_sugar': 5,
            'fat_saturated': 3.1415,
            'fibres': 2.1,
            'protein': 30,
            'carbohydrates': 10}


class AddIngredientTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding an ingredient
    '''

    object_class = Ingredient
    url = 'ingredient-add'
    pk = 7
    data = {'name': 'A new ingredient',
            'sodium': 2,
            'energy': 200,
            'fat': 10,
            'carbohydrates_sugar': 5,
            'fat_saturated': 3.1415,
            'fibres': 2.1,
            'protein': 30,
            'carbohydrates': 10}


class IngredientDetailTestCase(WorkoutManagerTestCase):
    '''
    Tests the ingredient details page
    '''

    def ingredient_detail(self, editor=False):
        '''
        Tests the ingredient details page
        '''

        response = self.client.get(reverse('wger.nutrition.views.ingredient.ingredient_view',
                                   kwargs={'id': 6}))
        self.assertEqual(response.status_code, 200)

        # Correct tab is selected
        self.assertEqual(response.context['active_tab'], NUTRITION_TAB)
        self.assertTrue(response.context['ingredient'])

        # Only authorized users see the edit links
        if editor:
            self.assertContains(response, 'Edit ingredient')
            self.assertContains(response, 'Delete ingredient')
        else:
            self.assertNotContains(response, 'Edit ingredient')
            self.assertNotContains(response, 'Delete ingredient')

        # Non-existent ingredients throw a 404.
        response = self.client.get(reverse('wger.nutrition.views.ingredient.ingredient_view',
                                   kwargs={'id': 42}))
        self.assertEqual(response.status_code, 404)

    def test_ingredient_detail_editor(self):
        '''
        Tests the ingredient details page as a logged in user with editor rights
        '''

        self.user_login('admin')
        self.ingredient_detail(editor=True)

    def test_ingredient_detail_non_editor(self):
        '''
        Tests the ingredient details page as a logged in user without editor rights
        '''

        self.user_login('test')
        self.ingredient_detail(editor=False)

    def test_ingredient_detail_logged_out(self):
        '''
        Tests the ingredient details page as an anonymous (logged out) user
        '''

        self.ingredient_detail(editor=False)
