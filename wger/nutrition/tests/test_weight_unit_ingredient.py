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

# Django
from django.urls import reverse_lazy

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
)
from wger.nutrition.models import IngredientWeightUnit


class WeightUnitIngredientRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(str(IngredientWeightUnit.objects.get(pk=1)), 'Spoon (109g)')


class AddWeightUnitIngredientTestCase(WgerAddTestCase):
    """
    Tests adding a new weight unit to an ingredient
    """

    object_class = IngredientWeightUnit
    url = reverse_lazy('nutrition:unit_ingredient:add', kwargs={'ingredient_pk': 1})
    data = {
        'name': 'Cup',
        'gram': 123,
    }


class DeleteWeightUnitIngredientTestCase(WgerDeleteTestCase):
    """
    Tests deleting a weight unit from an ingredient
    """

    object_class = IngredientWeightUnit
    url = 'nutrition:unit_ingredient:delete'
    pk = 1


class EditWeightUnitTestCase(WgerEditTestCase):
    """
    Tests editing a weight unit from an ingredient
    """

    object_class = IngredientWeightUnit
    url = 'nutrition:unit_ingredient:edit'
    pk = 1
    data = {
        'name': 'Tablespoon',
        'gram': 10,
    }


class WeightUnitToIngredientApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the weight unit to ingredient API resource
    """

    pk = 1
    resource = IngredientWeightUnit
    private_resource = False
    data = {
        'gram': 240,
        'id': 1,
        'ingredient': '1',
        'name': 'Spoon',
    }
