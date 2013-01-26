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

from django.core.urlresolvers import reverse

from wger.manager.models import Day

from wger.manager.tests.testcase import WorkoutManagerTestCase


class AddWorkoutDayTestCase(WorkoutManagerTestCase):
    '''
    Tests adding a day to a workout
    '''

    def add_day(self, fail=False):
        '''
        Helper function to test adding a day to a workout
        '''

        # Fetch the day edit page
        response = self.client.get(reverse('day-add', kwargs={'workout_pk': 3}))

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)

        # Edit the day
        response = self.client.post(reverse('day-add', kwargs={'workout_pk': 3}),
                                    {'description': 'a new day',
                                    'day': [1, 4]})
        if fail:
            self.assertRaises(Day.DoesNotExist, Day.objects.get, pk=6)
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

        else:
            day = Day.objects.get(pk=6)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(day.description, 'a new day')
            self.assertEqual(len(day.day.all()), 2)
            self.assertEqual(day.day.all()[0].day_of_week, 'Monday')
            self.assertEqual(day.day.all()[1].day_of_week, 'Thursday')

    def test_add_day_anonymous(self):
        '''
        Test adding a day to a workout as an anonymous user
        '''

        self.add_day(fail=True)

    def test_add_workout_owner(self):
        '''
        Test adding a day to a workout as the owner user
        '''

        self.user_login('test')
        self.add_day(fail=False)

    def test_add_workout_other(self):
        '''
        Test adding a day to a workout a different logged in user
        '''

        self.user_login('admin')
        self.add_day(fail=True)


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
        response = self.client.get(reverse('wger.manager.views.delete_day', kwargs={'id': 3,
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


class EditWorkoutDayTestCase(WorkoutManagerTestCase):
    '''
    Tests editing the day of a Workout
    '''

    def edit_day(self, fail=False):
        '''
        Helper function to test editing the day
        '''

        # Fetch the day edit page
        response = self.client.get(reverse('day-edit', kwargs={'pk': 5}))

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)

        # Edit the day
        response = self.client.post(reverse('day-edit', kwargs={'pk': 5}),
                                    {'description': 'a different description',
                                    'day': [1, 4]})

        day = Day.objects.get(pk=5)

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')
            self.assertEqual(day.description, 'A cool day')
            self.assertEqual(len(day.day.all()), 1)
            self.assertEqual(day.day.all()[0].day_of_week, 'Friday')

        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(day.description, 'a different description')
            self.assertEqual(len(day.day.all()), 2)
            self.assertEqual(day.day.all()[0].day_of_week, 'Monday')
            self.assertEqual(day.day.all()[1].day_of_week, 'Thursday')

    def test_edit_day_anonymous(self):
        '''
        Test editing the day of a workout as an anonymous user
        '''

        self.edit_day(fail=True)

    def test_create_workout_owner(self):
        '''
        Test editing the day of a workout as the owner user
        '''

        self.user_login('test')
        self.edit_day(fail=False)

    def test_create_workout_other(self):
        '''
        Test editing the day of a workout a logged in user
        '''

        self.user_login('admin')
        self.edit_day(fail=True)


class RenderWorkoutDayTestCase(WorkoutManagerTestCase):
    '''
    Tests rendering a single workout day
    '''

    def render_day(self, fail=False):
        '''
        Helper function to test rendering a single workout day
        '''

        # Fetch the day edit page
        response = self.client.get(reverse('wger.manager.views.view_day', kwargs={'id': 5}))

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
