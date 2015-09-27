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
from django.core.cache import cache
from wger.core.tests import api_base_test

from wger.exercises.models import Equipment, Exercise

from wger.manager.tests.testcase import (
    WorkoutManagerTestCase,
    WorkoutManagerDeleteTestCase,
    WorkoutManagerEditTestCase,
    WorkoutManagerAddTestCase
)
from wger.utils.cache import get_template_cache_name, cache_mapper
from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE


class EquipmentRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(Equipment.objects.get(pk=1)), 'Dumbbells')


class EquipmentShareButtonTestCase(WorkoutManagerTestCase):
    '''
    Test that the share button is correctly displayed and hidden
    '''

    def test_share_button(self):
        url = reverse('exercise:equipment:overview')

        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('admin')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('test')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])


class AddEquipmentTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new equipment
    '''

    object_class = Equipment
    url = 'exercise:equipment:add'
    data = {'name': 'A new equipment'}


class DeleteEquipmentTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting an equipment
    '''

    object_class = Equipment
    url = 'exercise:equipment:delete'
    pk = 1


class EditEquipmentTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing an equipment
    '''

    object_class = Equipment
    url = 'exercise:equipment:edit'
    pk = 1
    data = {'name': 'A new name'}


class EquipmentListTestCase(WorkoutManagerTestCase):
    '''
    Tests the equipment list page (admin view)
    '''

    def test_overview(self):

        # Add more equipments so we can test the pagination
        self.user_login('admin')
        data = {"name": "A new entry"}
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


class EquipmentCacheTestCase(WorkoutManagerTestCase):
    '''
    Equipment cache test case
    '''

    def test_equipment_overview(self):
        '''
        Test the equipment overview cache is correctly generated on visit
        '''
        if self.is_mobile:
            self.client.get(reverse('exercise:equipment:overview'))
        else:
            self.assertFalse(cache.get(get_template_cache_name('equipment-overview', 2)))
            self.client.get(reverse('exercise:equipment:overview'))
            self.assertTrue(cache.get(get_template_cache_name('equipment-overview', 2)))

    def test_equipmet_cache_update(self):
        '''
        Test that the template cache for the overview is correctly reseted when
        performing certain operations
        '''

        self.assertFalse(cache.get(get_template_cache_name('equipment-overview', 2)))

        self.client.get(reverse('exercise:equipment:overview'))
        self.client.get(reverse('exercise:exercise:view', kwargs={'id': 2}))

        old_exercise = cache.get(cache_mapper.get_exercise_key(2))
        old_overview = cache.get(get_template_cache_name('equipment-overview', 2))

        exercise = Exercise.objects.get(pk=2)
        exercise.name = 'Very cool exercise 2'
        exercise.description = 'New description'
        exercise.equipment.add(Equipment.objects.get(pk=2))
        exercise.save()

        self.assertFalse(cache.get(get_template_cache_name('equipment-overview', 2)))

        self.client.get(reverse('exercise:equipment:overview'))
        self.client.get(reverse('exercise:exercise:view', kwargs={'id': 2}))

        new_exercise = cache.get(cache_mapper.get_exercise_key(2))
        new_overview = cache.get(get_template_cache_name('equipment-overview', 2))

        self.assertNotEqual(old_exercise.name, new_exercise.name)
        self.assertNotEqual(old_overview, new_overview)


class EquipmentApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the equipment overview resource
    '''
    pk = 1
    resource = Equipment
    private_resource = False
