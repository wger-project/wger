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
        count_before = TrainingSchedule.objects.count()
        response = self.client.post(reverse('workout-copy', kwargs={'pk': '3'}),
                                    {'comment': 'A copied workout'})
        count_after = TrainingSchedule.objects.count()

        if not logged_in:
            self.assertEqual(count_before, count_after)
        else:
            self.assertGreater(count_after, count_before)
            self.assertEqual(count_after, 4)

            self.assertTemplateUsed('workout/view.html')

        # Test accessing the copied workout
        response = self.client.get(reverse('wger.manager.views.view_workout', kwargs={'id': 4}))

        if not logged_in:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 200)

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
