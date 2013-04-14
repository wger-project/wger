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

import logging

from django.core.urlresolvers import reverse

from wger.manager.models import Workout
from wger.manager.tests.testcase import WorkoutManagerTestCase

logger = logging.getLogger('workout_manager.custom')


class CopyWorkoutTestCase(WorkoutManagerTestCase):
    '''
    Tests copying a workout
    '''

    def copy_workout(self, logged_in=False):
        '''
        Helper function to test copying workouts
        '''

        # Open the copy workout form
        response = self.client.get(reverse('workout-copy', kwargs={'pk': '3'}))
        if not logged_in:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 200)

        # Copy the workout
        count_before = Workout.objects.count()
        response = self.client.post(reverse('workout-copy', kwargs={'pk': '3'}),
                                    {'comment': 'A copied workout'})
        count_after = Workout.objects.count()

        if not logged_in:
            self.assertEqual(count_before, count_after)
        else:
            self.assertGreater(count_after, count_before)
            self.assertEqual(count_after, 4)

            self.assertTemplateUsed('workout/view.html')

        # Test accessing the copied workout
        response = self.client.get(reverse('wger.manager.views.workout.view',
                                           kwargs={'id': 4}))

        if not logged_in:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 200)

            original = Workout.objects.get(pk=3)
            copy = Workout.objects.get(pk=4)

            days_original = original.day_set.all()
            days_copy = copy.day_set.all()

            # Test that the different attributes and objects are correctly copied over
            for i in range(0, original.day_set.count()):
                self.assertEqual(days_original[i].description, days_copy[i].description)

                for j in range(0, days_original[i].day.count()):
                    self.assertEqual(days_original[i].day.all()[j], days_copy[i].day.all()[j])

                sets_original = days_original[i].set_set.all()
                sets_copy = days_copy[i].set_set.all()

                for j in range(days_original[i].set_set.count()):
                    sets_original_id = sets_original[j].id
                    sets_copy_id = sets_copy[j].id

                    self.assertEqual(sets_original[j].sets, sets_copy[j].sets)
                    self.assertEqual(sets_original[j].order, sets_copy[j].order)

                    exercises_original = sets_original[j].exercises.all()
                    exercises_copy = sets_copy[j].exercises.all()

                    for k in range(sets_original[j].exercises.count()):
                        self.assertEqual(exercises_original[k], exercises_copy[k])

    def test_copy_workout_anonymous(self):
        '''
        Test copying a workout as anonymous user
        '''

        self.copy_workout()

    def test_copy_workout_logged_in(self):
        '''
        Test copying a workout as a logged in user
        '''

        self.user_login('test')
        self.copy_workout(logged_in=True)
