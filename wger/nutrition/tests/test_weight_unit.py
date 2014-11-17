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

from wger.nutrition.models import WeightUnit

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase

from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE


class AddWeightUnitTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new weight unit
    '''

    object_class = WeightUnit
    url = 'weight-unit-add'
    data = {'name': 'A new weight unit'}


class DeleteWeightUnitTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a weight unit
    '''

    object_class = WeightUnit
    url = 'weight-unit-delete'
    pk = 1


class EditWeightUnitTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a weight unit
    '''

    object_class = WeightUnit
    url = 'weight-unit-edit'
    pk = 1
    data = {'name': 'A new name'}


class WeightUnitOverviewTestCase(WorkoutManagerTestCase):
    '''
    Tests the ingredient unit overview page
    '''

    def test_overview(self):

        # Add more ingredient units so we can test the pagination
        self.user_login('admin')
        data = {"name": "A new, cool unit",
                "language": 2}
        for i in range(0, 50):
            self.client.post(reverse('weight-unit-add'), data)

        # Page exists and the pagination works
        response = self.client.get(reverse('weight-unit-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['unit_list']), PAGINATION_OBJECTS_PER_PAGE)

        response = self.client.get(reverse('weight-unit-list'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['unit_list']), PAGINATION_OBJECTS_PER_PAGE)

        response = self.client.get(reverse('weight-unit-list'), {'page': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['unit_list']), 3)

        # 'last' is a special case
        response = self.client.get(reverse('weight-unit-list'), {'page': 'last'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['unit_list']), 3)

        # Page does not exist
        response = self.client.get(reverse('weight-unit-list'), {'page': 100})
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('weight-unit-list'), {'page': 'foobar'})
        self.assertEqual(response.status_code, 404)


class WeightUnitApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the weight unit overview resource
    '''
    pk = 1
    resource = WeightUnit
    private_resource = False
    data = {'name': 'The weight unit name'}
