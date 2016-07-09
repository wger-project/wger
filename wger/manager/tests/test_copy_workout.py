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

import logging

from django.core.urlresolvers import reverse

from wger.core.models import UserProfile
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.manager.models import Workout

logger = logging.getLogger(__name__)


class CopyWorkoutTestCase(WorkoutManagerTestCase):
    '''
    Tests copying a workout
    '''

    def copy_workout(self, owner=False):
        '''
        Helper function to test copying workouts
        '''

        # Open the copy workout form
        response = self.client.get(reverse('manager:workout:copy', kwargs={'pk': '3'}))
        if not owner:
            self.assertEqual(response.status_code, 404)
        else:
            self.assertEqual(response.status_code, 200)

        # Copy the workout
        count_before = Workout.objects.count()
        response = self.client.post(reverse('manager:workout:copy', kwargs={'pk': '3'}),
                                    {'comment': 'A copied workout'})
        count_after = Workout.objects.count()

        if not owner:
            self.assertEqual(count_before, count_after)
        else:
            self.assertGreater(count_after, count_before)
            self.assertEqual(count_after, 4)

            self.assertTemplateUsed('workout/view.html')

        # Test accessing the copied workout
        response = self.client.get(reverse('manager:workout:view', kwargs={'pk': 4}))

        if not owner:
            self.assertEqual(response.status_code, 404)
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

                    self.assertEqual(sets_original[j].sets, sets_copy[j].sets)
                    self.assertEqual(sets_original[j].order, sets_copy[j].order)

                    exercises_original = sets_original[j].exercises.all()
                    exercises_copy = sets_copy[j].exercises.all()

                    for k in range(sets_original[j].exercises.count()):
                        self.assertEqual(exercises_original[k], exercises_copy[k])

    def test_copy_workout_owner(self):
        '''
        Test copying a workout as the owner user
        '''

        self.user_login('test')
        self.copy_workout(owner=True)

    def test_copy_shared_not_allowed(self):
        '''
        Test copying a workout from another shared user where user does not share workouts
        '''
        profile = UserProfile.objects.get(user__username='test')
        profile.ro_access = False
        profile.save()

        self.user_login('admin')
        response = self.client.get(reverse('manager:workout:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 403)

    def test_copy_shared_allowed(self):
        '''
        Test copying a workout from another shared user where user does share workouts
        '''
        profile = UserProfile.objects.get(user__username='test')
        profile.ro_access = True
        profile.save()

        self.user_login('admin')
        response = self.client.get(reverse('manager:workout:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 200)
