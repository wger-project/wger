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


from django.core.urlresolvers import reverse
from django.core.cache import cache

from wger.exercises.models import Muscle

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import ApiBaseResourceTestCase
from wger.utils.cache import get_template_cache_name


class AddMuscleTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a muscle
    '''

    object_class = Muscle
    url = 'muscle-add'
    pk = 4
    data = {'name': 'A new muscle',
            'is_front': True}


class EditMuscleTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a muscle
    '''

    object_class = Muscle
    url = 'muscle-edit'
    pk = 1
    data = {'name': 'The new name',
            'is_front': True}


class DeleteMuscleTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a muscle
    '''

    object_class = Muscle
    url = 'muscle-delete'
    pk = 1


class MuscleCacheTestCase(WorkoutManagerTestCase):
    '''
    Muscle cache test case
    '''

    def test_overview(self):
        '''
        Test the muscle overview cache is correctly generated on visit
        '''

        if not self.is_mobile:
            self.assertFalse(cache.get(get_template_cache_name('muscle-overview', 2)))
            self.client.get(reverse('muscle-overview'))
            self.assertTrue(cache.get(get_template_cache_name('muscle-overview', 2)))


class MuscleOverviewTestCase(WorkoutManagerTestCase):
    '''
    Test that only admins see the edit links
    '''

    def test_overview(self):
        '''
        Test that only admins see the edit links
        '''

        self.user_login('admin')
        response = self.client.get(reverse('muscle-overview'))
        self.assertContains(response, 'Edit muscle')
        self.assertContains(response, 'Delete muscle')
        self.assertContains(response, 'Add muscle')
        self.assertContains(response, 'After adding a muscle')

        self.user_logout()
        response = self.client.get(reverse('muscle-overview'))
        self.assertNotContains(response, 'Edit muscle')
        self.assertNotContains(response, 'Delete muscle')
        self.assertNotContains(response, 'Add muscle')
        self.assertNotContains(response, 'After adding a muscle')


class MuscleApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests the muscle overview resource
    '''
    resource = 'muscle'
    user = None
    resource_updatable = False


class MuscleDetailApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests accessing a specific muscle
    '''
    resource = 'muscle/1'
    user = None
    resource_updatable = False
