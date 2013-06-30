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

import json

from django.core import mail
from django.core.urlresolvers import reverse

from wger.exercises.models import Exercise
from wger.exercises.models import ExerciseCategory

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase


class ExerciseIndexTestCase(WorkoutManagerTestCase):

    def exercise_index(self, logged_in=True, demo=False, admin=False):
        '''
        Tests the exercise overview page
        '''

        response = self.client.get(reverse('wger.exercises.views.exercises.overview'))

        # Page exists
        self.assertEqual(response.status_code, 200)

        # Correct tab is selected
        self.assertEqual(response.context['active_tab'], 'exercises')

        # Correct categories are shown
        category_1 = response.context['categories'][0]
        self.assertEqual(category_1.id, 2)
        self.assertEqual(category_1.name, "Another category")

        category_2 = response.context['categories'][1]
        self.assertEqual(category_2.id, 1)
        self.assertEqual(category_2.name, "Category")

        # Correct exercises in the categories
        exercises_1 = category_1.exercise_set.all()
        exercise_1 = exercises_1[0]
        exercise_2 = exercises_1[1]
        self.assertEqual(exercise_1.id, 1)
        self.assertEqual(exercise_1.name, "An exercise")

        self.assertEqual(exercise_2.id, 2)
        self.assertEqual(exercise_2.name, "Very cool exercise")

        self.assertContains(response, 'Add new exercise')

        # Only authorized users see the edit links
        if admin:
            self.assertNotContains(response, 'Only registered users can do this')
            self.assertContains(response, 'Edit category')
            self.assertContains(response, 'Delete category')
            self.assertContains(response, 'Add category')
        else:
            self.assertNotContains(response, 'Edit category')
            self.assertNotContains(response, 'Delete category')
            self.assertNotContains(response, 'Add category')

        if logged_in and not demo:
            self.assertNotContains(response, 'Only registered users can do this')

        if logged_in and demo:
            self.assertContains(response, 'Only registered users can do this')

    def test_exercise_index_editor(self):
        '''
        Tests the exercise overview page as a logged in user with editor rights
        '''

        self.user_login('admin')
        self.exercise_index(admin=True)

    def test_exercise_index_non_editor(self):
        '''
        Tests the exercise overview page as a logged in user without editor rights
        '''

        self.user_login('test')
        self.exercise_index()

    def test_exercise_index_demo_user(self):
        '''
        Tests the exercise overview page as a logged in demo user
        '''

        self.user_login('demo')
        self.exercise_index(demo=True)

    def test_exercise_index_logged_out(self):
        '''
        Tests the exercise overview page as an anonymous (logged out) user
        '''

        self.exercise_index(logged_in=False)

    def test_empty_exercise_index(self):
        '''
        Test the index when there are no categories
        '''
        self.user_login('admin')
        ExerciseCategory.objects.all().delete()
        response = self.client.get(reverse('wger.exercises.views.exercises.overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No categories')


class ExerciseDetailTestCase(WorkoutManagerTestCase):
    '''
    Tests the exercise details page
    '''

    def exercise_detail(self, editor=False):
        '''
        Tests the exercise details page
        '''

        response = self.client.get(reverse('wger.exercises.views.exercises.view',
                                   kwargs={'id': 1}))
        self.assertEqual(response.status_code, 200)

        # Correct tab is selected
        self.assertEqual(response.context['active_tab'], 'exercises')

        # Exercise loaded correct muscles
        exercise_1 = response.context['exercise']
        self.assertEqual(exercise_1.id, 1)

        muscles = exercise_1.muscles.all()
        muscle_1 = muscles[0]
        muscle_2 = muscles[1]

        self.assertEqual(muscle_1.id, 1)
        self.assertEqual(muscle_2.id, 2)

        # Only authorized users see the edit links
        if editor:
            self.assertContains(response, 'Edit')
            self.assertContains(response, 'Delete')
            self.assertContains(response, 'Add new comment')
            self.assertNotContains(response, 'Exercise is pending')
        else:
            self.assertNotContains(response, 'Edit')
            self.assertNotContains(response, 'Delete')
            self.assertNotContains(response, 'Add new comment')
            self.assertNotContains(response, 'Exercise is pending')

        # Ensure that non-existent exercises throw a 404.
        response = self.client.get(reverse('wger.exercises.views.exercises.view',
                                   kwargs={'id': 42}))
        self.assertEqual(response.status_code, 404)

    def test_exercise_detail_editor(self):
        '''
        Tests the exercise details page as a logged in user with editor rights
        '''

        self.user_login('admin')
        self.exercise_detail(editor=True)

    def test_exercise_detail_non_editor(self):
        '''
        Tests the exercise details page as a logged in user without editor rights
        '''

        self.user_login('test')
        self.exercise_detail(editor=False)

    def test_exercise_detail_logged_out(self):
        '''
        Tests the exercise details page as an anonymous (logged out) user
        '''

        self.exercise_detail(editor=False)


class ExercisesTestCase(WorkoutManagerTestCase):
    '''
    Exercise test case
    '''

    def add_exercise_user_fail(self):
        '''
        Helper function to test adding exercises by users that aren't authorized
        '''

        # Add an exercise
        count_before = Exercise.objects.count()
        response = self.client.post(reverse('exercise-add'),
                                    {'category': 2,
                                    'name': 'my test exercise',
                                    'muscles': [1, 2]})
        count_after = Exercise.objects.count()

        # Exercise was not added
        self.assertEqual(count_before, count_after)

    def test_add_exercise_temp_user(self):
        '''
        Tests adding an exercise with a logged in demo user
        '''

        self.user_login('demo')
        self.add_exercise_user_fail()

    def test_add_exercise_no_user(self):
        '''
        Tests adding an exercise with a logged out (anonymous) user
        '''

        self.user_logout()
        self.add_exercise_user_fail()
        self.user_logout()

    def add_exercise_success(self, admin=False):
        '''
        Tests adding/editing an exercise with a user with enough rights to do this
        '''

        # Add an exercise
        count_before = Exercise.objects.count()
        response = self.client.post(reverse('exercise-add'),
                                    {'category': 2,
                                    'name': 'my test exercise',
                                    'description': 'a nice, long and accurate description',
                                    'muscles': [1, 2]})
        count_after = Exercise.objects.count()
        self.assertEqual(response.status_code, 302)
        new_location = response['Location']
        self.assertEqual(count_before + 1, count_after, 'Exercise was not added')

        response = self.client.get(new_location)
        exercise_id = response.context['exercise'].id

        # Exercise was saved
        exercise = Exercise.objects.get(pk=exercise_id)
        if admin:
            self.assertEqual(exercise.user_id, 1)
            self.assertEqual(exercise.status, Exercise.EXERCISE_STATUS_ADMIN)
        else:
            self.assertEqual(exercise.user_id, 2)
            self.assertEqual(exercise.status, Exercise.EXERCISE_STATUS_PENDING)

        response = self.client.get(reverse('wger.exercises.views.exercises.view',
                                   kwargs={'id': exercise_id}))
        self.assertEqual(response.status_code, 200)

        # Navigation tab
        self.assertEqual(response.context['active_tab'], 'exercises')

        exercise_1 = Exercise.objects.get(pk=exercise_id)
        self.assertEqual(exercise_1.name, 'my test exercise')

        # Wrong category - adding
        response = self.client.post(reverse('exercise-add'),
                                    {'category': 111,
                                    'name': 'my test exercise',
                                    'muscles': [1, 2]})
        self.assertTrue(response.context['form'].errors['category'])

        # Wrong category - editing
        response = self.client.post(reverse('exercise-edit', kwargs={'pk': '1'}),
                                    {'category': 111,
                                    'name': 'my test exercise',
                                    'muscles': [1, 2]})
        if admin:
            self.assertTrue(response.context['form'].errors['category'])
        else:
            self.assertEqual(response.status_code, 302)

        # No muscles - adding
        response = self.client.post(reverse('exercise-add'),
                                    {'category': 1,
                                    'name': 'my test exercise',
                                    'muscles': []})
        self.assertTrue(response.context['form'].errors['muscles'])

        # No muscles - editing
        response = self.client.post(reverse('exercise-edit', kwargs={'pk': '1'}),
                                    {'category': 1,
                                    'name': 'my test exercise',
                                    'muscles': []})
        if admin:
            self.assertTrue(response.context['form'].errors['muscles'])
        else:
            self.assertEqual(response.status_code, 302)

    def test_add_exercise_success(self):
        '''
        Tests adding/editing an exercise with a user with enough rights to do this
        '''
        self.user_login('admin')
        self.add_exercise_success(admin=True)

    def test_add_exercise_user_no_rights(self):
        '''
        Tests adding an exercise with a user without enough rights to do this
        '''
        self.user_login('test')
        self.add_exercise_success(admin=False)
        self.assertEqual(len(mail.outbox), 1)

    def search_exercise(self, fail=True):
        '''
        Helper function to test searching for exercises
        '''

        # Search for exercises (1 hit, "Very cool exercise")
        response = self.client.get(reverse('wger.exercises.views.exercises.search'),
                                   {'term': 'cool'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['exercises']), 1)
        self.assertEqual(response.context['exercises'][0].name, 'Very cool exercise')

        # Search for a pending exercise (0 hits, "Pending exercise")
        response = self.client.get(reverse('wger.exercises.views.exercises.search'),
                                   {'term': 'Pending'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['exercises']), 0)

        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        # AJAX-Search for exercises (1 hit, "Very cool exercise")
        response = self.client.get(reverse('wger.exercises.views.exercises.search'),
                                   {'term': 'cool'},
                                   **kwargs)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['value'], 'Very cool exercise')

        # AJAX Search for a pending exercise (0 hits, "Pending exercise")
        response = self.client.get(reverse('wger.exercises.views.exercises.search'),
                                   {'term': 'Pending'},
                                   **kwargs)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(len(result), 0)

    def test_search_exercise_anonymous(self):
        '''
        Test deleting an exercise by an anonymous user
        '''

        self.search_exercise()

    def test_search_exercise_logged_in(self):
        '''
        Test deleting an exercise by a logged in user
        '''

        self.user_login('test')
        self.search_exercise()


class DeleteExercisesTestCase(WorkoutManagerDeleteTestCase):
    '''
    Exercise test case
    '''

    object_class = Exercise
    url = 'exercise-delete'
    pk = 2
    user_success = 'admin'
    user_fail = 'test'
