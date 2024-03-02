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
from django.urls import reverse

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
)
from wger.exercises.models import Equipment
from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE


class EquipmentRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(str(Equipment.objects.get(pk=1)), 'Dumbbells')


class AddEquipmentTestCase(WgerAddTestCase):
    """
    Tests adding a new equipment
    """

    object_class = Equipment
    url = 'exercise:equipment:add'
    data = {'name': 'A new equipment'}


class DeleteEquipmentTestCase(WgerDeleteTestCase):
    """
    Tests deleting an equipment
    """

    object_class = Equipment
    url = 'exercise:equipment:delete'
    pk = 1


class EditEquipmentTestCase(WgerEditTestCase):
    """
    Tests editing an equipment
    """

    object_class = Equipment
    url = 'exercise:equipment:edit'
    pk = 1
    data = {'name': 'A new name'}


class EquipmentListTestCase(WgerTestCase):
    """
    Tests the equipment list page (admin view)
    """

    def test_overview(self):
        # Add more equipments so we can test the pagination
        self.user_login('admin')
        data = {'name': 'A new entry'}
        for i in range(0, 50):
            self.client.post(reverse('exercise:equipment:add'), data)

        # Page exists and the pagination works
        response = self.client.get(reverse('exercise:equipment:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['equipment_list']), PAGINATION_OBJECTS_PER_PAGE)

        response = self.client.get(reverse('exercise:equipment:list'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['equipment_list']), PAGINATION_OBJECTS_PER_PAGE)

        response = self.client.get(reverse('exercise:equipment:list'), {'page': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['equipment_list']), 3)

        # 'last' is a special case
        response = self.client.get(reverse('exercise:equipment:list'), {'page': 'last'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['equipment_list']), 3)

        # Page does not exist
        response = self.client.get(reverse('exercise:equipment:list'), {'page': 100})
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('exercise:equipment:list'), {'page': 'foobar'})
        self.assertEqual(response.status_code, 404)


class EquipmentApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the equipment overview resource
    """

    pk = 1
    resource = Equipment
    private_resource = False
    overview_cached = True
