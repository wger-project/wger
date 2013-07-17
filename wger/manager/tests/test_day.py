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

from wger.manager.models import Day

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.utils.cache import get_template_cache_name


class AddWorkoutDayTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a day to a workout
    '''

    object_class = Day
    url = reverse('day-add', kwargs={'workout_pk': 3})
    pk = 6
    user_success = 'test'
    user_fail = 'admin'
    data = {'description': 'a new day',
            'day': [1, 4]}


class DeleteWorkoutDayTestCase(WorkoutManagerTestCase):
    '''
    Tests deleting a day
    '''

    def delete_day(self, fail=False):
        '''
        Helper function to test deleting a day
        '''

        # Fetch the day edit page
        count_before = Day.objects.count()
        response = self.client.get(reverse('wger.manager.views.day.delete', kwargs={'id': 3,
                                           'day_id': 5}))
        count_after = Day.objects.count()

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')
            self.assertEqual(count_before, count_after)

        else:
            self.assertRaises(Day.DoesNotExist, Day.objects.get, pk=5)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_before - 1, count_after)

    def test_delete_day_anonymous(self):
        '''
        Test deleting a day as an anonymous user
        '''

        self. delete_day(fail=True)

    def test_delete_workout_owner(self):
        '''
        Test deleting a day as the owner user
        '''

        self.user_login('test')
        self.delete_day(fail=False)

    def test_delete_workout_other(self):
        '''
        Test deleting a day as a different logged in user
        '''

        self.user_login('admin')
        self.delete_day(fail=True)


class EditWorkoutDayTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing the day of a Workout
    '''

    object_class = Day
    url = 'day-edit'
    pk = 5
    user_success = 'test'
    user_fail = 'admin'
    data = {'description': 'a different description',
            'day': [1, 4]}


class RenderWorkoutDayTestCase(WorkoutManagerTestCase):
    '''
    Tests rendering a single workout day
    '''

    def render_day(self, fail=False):
        '''
        Helper function to test rendering a single workout day
        '''

        # Fetch the day edit page
        response = self.client.get(reverse('wger.manager.views.day.view', kwargs={'id': 5}))

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed('day/view.html')

    def test_render_day_anonymous(self):
        '''
        Test rendering a single workout day as an anonymous user
        '''

        self.render_day(fail=True)

    def test_render_workout_owner(self):
        '''
        Test rendering a single workout day as the owner user
        '''

        self.user_login('test')
        self.render_day(fail=False)

    def test_render_workout_other(self):
        '''
        Test rendering a single workout day as a different logged in user
        '''

        self.user_login('admin')
        self.render_day(fail=True)


class WorkoutCacheTestCase(WorkoutManagerTestCase):
    '''
    Workout cache test case
    '''

    def test_workout_view_day(self):
        '''
        Test the workout view cache is correctly generated on visit
        '''

        self.user_login('admin')
        self.client.get(reverse('wger.manager.views.workout.view', kwargs={'id': 1}))

        old_day1 = cache.get(get_template_cache_name('day-view', 1))
        old_day2 = cache.get(get_template_cache_name('day-view', 2))
        self.assertTrue(old_day1)
        self.assertTrue(old_day2)

        day1 = Day.objects.get(pk=1)
        day1.description = 'A new name'
        day1.save()
        self.assertFalse(cache.get(get_template_cache_name('day-view', 1)))
        self.assertTrue(cache.get(get_template_cache_name('day-view', 2)))

        self.client.get(reverse('wger.manager.views.workout.view', kwargs={'id': 1}))
        new_day1 = cache.get(get_template_cache_name('day-view', 1))
        new_day2 = cache.get(get_template_cache_name('day-view', 2))
        self.assertNotEqual(old_day1, new_day1)
        self.assertEqual(old_day2, new_day2)

        day1.delete()
        self.assertFalse(cache.get(get_template_cache_name('day-view', 1)))
        self.assertTrue(cache.get(get_template_cache_name('day-view', 2)))
