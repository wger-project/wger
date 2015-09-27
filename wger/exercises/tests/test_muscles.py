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
from wger.core.tests import api_base_test

from wger.exercises.models import Muscle

from wger.manager.tests.testcase import (
    WorkoutManagerTestCase,
    WorkoutManagerDeleteTestCase,
    WorkoutManagerEditTestCase,
    WorkoutManagerAddTestCase,
)
from wger.utils.cache import get_template_cache_name


class MuscleRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(Muscle.objects.get(pk=1)), 'Anterior testoid')


class MusclesShareButtonTestCase(WorkoutManagerTestCase):
    '''
    Test that the share button is correctly displayed and hidden
    '''

    def test_share_button(self):
        url = reverse('exercise:muscle:overview')

        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('admin')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('test')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])


class AddMuscleTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a muscle
    '''

    object_class = Muscle
    url = 'exercise:muscle:add'
    data = {'name': 'A new muscle',
            'is_front': True}


class EditMuscleTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a muscle
    '''

    object_class = Muscle
    url = 'exercise:muscle:edit'
    pk = 1
    data = {'name': 'The new name',
            'is_front': True}


class DeleteMuscleTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a muscle
    '''

    object_class = Muscle
    url = 'exercise:muscle:delete'
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
            self.client.get(reverse('exercise:muscle:overview'))
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
        response = self.client.get(reverse('exercise:muscle:overview'))
        self.assertContains(response, 'Edit muscle')
        self.assertContains(response, 'Delete muscle')
        self.assertContains(response, 'Add muscle')
        self.assertContains(response, 'After adding a muscle')

        self.user_logout()
        response = self.client.get(reverse('exercise:muscle:overview'))
        self.assertNotContains(response, 'Edit muscle')
        self.assertNotContains(response, 'Delete muscle')
        self.assertNotContains(response, 'Add muscle')
        self.assertNotContains(response, 'After adding a muscle')


class MuscleApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the muscle overview resource
    '''
    pk = 1
    resource = Muscle
    private_resource = False
    data = {'name': 'The name',
            'is_front': True}
