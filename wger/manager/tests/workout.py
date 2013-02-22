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

from wger.manager.models import TrainingSchedule

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase


class AddWorkoutTestCase(WorkoutManagerTestCase):
    '''
    Tests adding a Workout
    '''

    def create_workout(self, logged_in=False):
        '''
        Helper function to test creating workouts
        '''

        # Create a workout
        count_before = TrainingSchedule.objects.count()
        response = self.client.get(reverse('wger.manager.views.add'))
        count_after = TrainingSchedule.objects.count()

        # There is always a redirect
        self.assertEqual(response.status_code, 302)

        # Test creating workout
        if not logged_in:

            self.assertEqual(count_before, count_after)
            self.assertEqual(count_after, 3)
            self.assertTemplateUsed('login.html')

        else:
            self.assertGreater(count_after, count_before)
            self.assertTemplateUsed('workout/view.html')

        # Test accessing workout
        response = self.client.get(reverse('wger.manager.views.view_workout', kwargs={'id': 1}))

        if logged_in:
            workout = TrainingSchedule.objects.get(pk=1)
            self.assertEqual(response.context['workout'], workout)
            self.assertEqual(response.status_code, 200)
        else:
            self.assertEqual(response.status_code, 302)
            #workout = TrainingSchedule.objects.get(pk = 1)

    def test_create_workout_anonymous(self):
        '''
        Test creating a workout as anonymous user
        '''

        self.user_logout()
        self.create_workout()

    def test_create_workout_logged_in(self):
        '''
        Test creating a workout a logged in user
        '''

        self.user_login()
        self.create_workout(logged_in=True)
        self.user_logout()


class DeleteTestWorkoutTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a Workout
    '''

    delete_class = TrainingSchedule
    delete_url = 'workout-delete'
    pk = 3
    user_success = 'test'
    user_fail = 'admin'


class EditWorkoutTestCase(WorkoutManagerEditTestCase):
    object_class = TrainingSchedule
    edit_url = 'workout-edit'
    pk = 3
    user_success = 'test'
    user_fail = 'admin'
    data_update = {'comment': 'A new comment'}


class WorkoutOverviewTestCase(WorkoutManagerTestCase):
    '''
    Tests the workout overview
    '''

    def get_workout_overview(self, logged_in=False):
        '''
        Helper function to test the workout overview
        '''

        response = self.client.get(reverse('wger.manager.views.overview'))

        # Page exists
        if logged_in:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['workouts']), 2)
        else:
            self.assertEqual(response.status_code, 302)

    def test_dashboard_anonymous(self):
        '''
        Test creating a workout as anonymous user
        '''

        self.get_workout_overview()

    def test_dashboard_logged_in(self):
        '''
        Test creating a workout a logged in user
        '''
        self.user_login()
        self.get_workout_overview(logged_in=True)
