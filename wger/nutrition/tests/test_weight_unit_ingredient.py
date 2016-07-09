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
from django.core.urlresolvers import reverse_lazy

from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WorkoutManagerAddTestCase
from wger.core.tests.base_testcase import WorkoutManagerDeleteTestCase
from wger.core.tests.base_testcase import WorkoutManagerEditTestCase
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.nutrition.models import IngredientWeightUnit
from wger.nutrition.models import WeightUnit


class WeightUnitIngredientRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(IngredientWeightUnit.objects.get(pk=1)), 'Spoon (109g)')


class AddWeightUnitIngredientTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new weight unit to an ingredient
    '''

    object_class = IngredientWeightUnit
    url = reverse_lazy('nutrition:unit_ingredient:add',
                       kwargs={'ingredient_pk': 1})
    data = {'unit': 5,
            'gram': 123,
            'amount': 1}


class DeleteWeightUnitIngredientTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a weight unit from an ingredient
    '''

    object_class = IngredientWeightUnit
    url = 'nutrition:unit_ingredient:delete'
    pk = 1


class EditWeightUnitTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a weight unit from an ingredient
    '''

    object_class = IngredientWeightUnit
    url = 'nutrition:unit_ingredient:edit'
    pk = 1
    data = {'unit': 5,
            'gram': 10,
            'amount': 0.3}


class WeightUnitFormTestCase(WorkoutManagerTestCase):
    '''
    Tests the form for the weight units
    '''

    def test_add_weight_unit(self):
        '''
        Tests the form in the add view
        '''
        self.user_login('admin')
        response = self.client.get(reverse('nutrition:unit_ingredient:add',
                                           kwargs={'ingredient_pk': 1}))

        choices = [text for value, text in response.context['form']['unit'].field.choices]
        for unit in WeightUnit.objects.all():
            if unit.language_id == 1:
                self.assertNotIn(unit.name, choices)
            else:
                self.assertIn(unit.name, choices)

    def test_edit_weight_unit(self):
        '''
        Tests that the form in the edit view only shows weight units in the user's language
        '''
        self.user_login('admin')
        response = self.client.get(reverse('nutrition:unit_ingredient:edit',
                                           kwargs={'pk': 1}))

        choices = [text for value, text in response.context['form']['unit'].field.choices]
        for unit in WeightUnit.objects.all():
            if unit.language_id == 1:
                self.assertNotIn(unit.name, choices)
            else:
                self.assertIn(unit.name, choices)


class WeightUnitToIngredientApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the weight unit to ingredient API resource
    '''
    pk = 1
    resource = IngredientWeightUnit
    private_resource = False
    data = {'amount': '1',
            'gram': 240,
            'id': 1,
            'ingredient': '1',
            'unit': '1'}
