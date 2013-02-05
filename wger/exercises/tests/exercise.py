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

from django.core.urlresolvers import reverse

from wger.exercises.models import Exercise

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase


class ExerciseIndexTestCase(WorkoutManagerTestCase):

    def test_exercise_index(self):
        '''
        Tests the exercise overview page
        '''

        response = self.client.get(reverse('wger.exercises.views.exercise_overview'))

        # Page exists
        self.assertEqual(response.status_code, 200)

        # Correct tab is selected
        self.assertEqual(response.context['active_tab'], 'exercises')

        # Correct categories are shown
        category_1 = response.context['categories'][0]
        self.assertEqual(category_1.id, 2)
        self.assertEqual(category_1.name, "Another category")

        category_2 = response.context['categories'][1]
        self.assertEqual(category_2.id, 3)
        self.assertEqual(category_2.name, "Yet another category")

        # Correct exercises in the categories
        exercises_1 = category_1.exercise_set.all()
        exercise_1 = exercises_1[0]
        exercise_2 = exercises_1[1]
        self.assertEqual(exercise_1.id, 2)
        self.assertEqual(exercise_1.name, "A very cool exercise")

        self.assertEqual(exercise_2.id, 1)
        self.assertEqual(exercise_2.name, "An exercise")

    def test_exercise_detail(self):
        '''
        Tests the exercise details page
        '''

        response = self.client.get(reverse('wger.exercises.views.exercise_view', kwargs={'id': 1}))
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

        # Ensure that non-existent exercises throw a 404.
        response = self.client.get(reverse('wger.exercises.views.exercise_view', kwargs={'id': 42}))
        self.assertEqual(response.status_code, 404)


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
        self.assertTrue('login' in response['location'])

    def test_add_exercise_user_no_rights(self):
        '''
        Tests adding an exercise with a user without enough rights to do this
        '''

        self.user_login('test')
        self.add_exercise_user_fail()
        self.user_logout()

    def test_add_exercise_no_user(self):
        '''
        Tests adding an exercise with a logged out (anonymous) user
        '''

        self.user_logout()
        self.add_exercise_user_fail()
        self.user_logout()

    def test_add_exercise_administrator_user(self):
        '''
        Tests adding/editing an exercise with a user with enough rights to do this
        '''

        # Log in as 'admin'
        self.user_login()

        # Add an exercise
        count_before = Exercise.objects.count()
        response = self.client.post(reverse('exercise-add'),
                                    {'category': 2,
                                    'name': 'my test exercise',
                                    'muscles': [1, 2]})
        count_after = Exercise.objects.count()
        self.assertEqual(response.status_code, 302)
        new_location = response['Location']
        self.assertEqual(count_before + 1, count_after, 'Exercise was not added')

        response = self.client.get(new_location)
        exercise_id = response.context['exercise'].id

        # Exercise was saved
        response = self.client.get(reverse('wger.exercises.views.exercise_view',
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
        self.assertTrue(response.context['form'].errors['category'])

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
        self.assertTrue(response.context['form'].errors['muscles'])
        self.user_logout()

    def search_exercise(self, fail=True):
        '''
        Helper function to test searching for exercises
        '''

        # Search for exercises (1 hit, "A very cool exercise")
        response = self.client.get(reverse('wger.exercises.views.exercise_search') + '?term=cool')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['exercises']), 1)
        self.assertEqual(response.context['exercises'][0].name, 'A very cool exercise')

        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        # AJAX-Search for exercises (1 hit, "A very cool exercise")
        response = self.client.get(reverse('wger.exercises.views.exercise_search') +
                                   '?term=cool', **kwargs)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['value'], 'A very cool exercise')

    def test_search_exercise_anonymous(self):
        '''
        Test deleting an exercise by an anonymous user
        '''

        self.search_exercise()

    def test_search_exercise_unauthorized(self):
        '''
        Test deleting an exercise by an unauthorized user
        '''

        self.user_login('test')
        self.search_exercise()
        self.user_logout()

    def test_search_exercise_authorized(self):
        '''
        Test deleting an exercise by an authorized user
        '''

        self.user_login()
        self.search_exercise(fail=False)
        self.user_logout()


class DeleteExercisesTestCase(WorkoutManagerDeleteTestCase):
    '''
    Exercise test case
    '''

    delete_class = Exercise
    delete_url = 'exercise-delete'
    pk = 2
    user_success = 'admin'
    user_fail = 'test'
