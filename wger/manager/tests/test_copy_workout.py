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

# Standard Library
import logging

# Django
from django.urls import reverse

# wger
from wger.core.models import UserProfile
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import Workout


logger = logging.getLogger(__name__)


class CopyWorkoutTestCase(WgerTestCase):
    """
    Tests copying a workout or template
    """

    def copy_workout(self):
        """
        Helper function to test copying workouts
        """

        # Open the copy workout form
        response = self.client.get(reverse('manager:workout:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 200)

        # Copy the workout
        count_before = Workout.objects.count()
        self.client.post(
            reverse('manager:workout:copy', kwargs={'pk': '3'}),
            {'name': 'A copied workout'},
        )
        count_after = Workout.objects.count()

        self.assertGreater(count_after, count_before)
        self.assertEqual(count_after, 4)
        self.assertTemplateUsed('workout/view.html')

        # Test accessing the copied workout
        response = self.client.get(reverse('manager:workout:view', kwargs={'pk': 4}))
        self.assertEqual(response.status_code, 200)

        workout_original = Workout.objects.get(pk=3)
        workout_copy = Workout.objects.get(pk=4)

        days_original = workout_original.day_set.all()
        days_copy = workout_copy.day_set.all()

        # Test that the different attributes and objects are correctly copied over
        for i in range(0, workout_original.day_set.count()):
            self.assertEqual(days_original[i].description, days_copy[i].description)

            for j in range(0, days_original[i].day.count()):
                self.assertEqual(days_original[i].day.all()[j], days_copy[i].day.all()[j])

            sets_original = days_original[i].set_set.all()
            sets_copy = days_copy[i].set_set.all()

            for j in range(days_original[i].set_set.count()):
                self.assertEqual(sets_original[j].sets, sets_copy[j].sets)
                self.assertEqual(sets_original[j].order, sets_copy[j].order)
                self.assertEqual(sets_original[j].comment, sets_copy[j].comment)

                bases_original = sets_original[j].exercise_bases
                bases_copy = sets_copy[j].exercise_bases

                for k in range(len(sets_original[j].exercise_bases)):
                    self.assertEqual(bases_original[k], bases_copy[k])

                settings_original = sets_original[j].setting_set.all()
                settings_copy = sets_copy[j].setting_set.all()

                for l in range(settings_original.count()):
                    setting_copy = settings_copy[l]
                    setting_orig = settings_original[l]

                    self.assertEqual(setting_orig.repetition_unit, setting_copy.repetition_unit)
                    self.assertEqual(setting_orig.weight_unit, setting_copy.weight_unit)
                    self.assertEqual(setting_orig.reps, setting_copy.reps)
                    self.assertEqual(setting_orig.weight, setting_copy.weight)
                    self.assertEqual(setting_orig.rir, setting_copy.rir)

    def test_copy_workout_owner(self):
        """
        Test copying a workout as the owner user
        """

        self.user_login('test')
        self.copy_workout()

    def test_copy_workout(self):
        """
        Test copying a workout (not template)
        """
        self.user_login('test')
        response = self.client.get(reverse('manager:workout:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 200)

    def test_copy_workout_other(self):
        """
        Test copying a workout (not template) from another user
        """
        self.user_login('admin')
        response = self.client.get(reverse('manager:workout:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 403)

    def test_copy_template_no_public_other_user(self):
        """
        Test copying a workout template that is not marked as public and belongs to another user
        """
        workout = Workout.objects.get(pk=3)
        workout.is_template = True
        workout.save()

        self.user_login('admin')
        response = self.client.get(reverse('manager:workout:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 403)

    def test_copy_template_no_public_owner_user(self):
        """
        Test copying a workout template that is not marked as public and belongs to the current user
        """
        workout = Workout.objects.get(pk=3)
        workout.is_template = True
        workout.save()

        self.user_login('test')
        response = self.client.get(reverse('manager:workout:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 200)

    def test_copy_template_public_other_user(self):
        """
        Test copying a workout template that is marked as public and belongs to another user
        """
        workout = Workout.objects.get(pk=3)
        workout.is_template = True
        workout.is_public = True
        workout.save()

        self.user_login('admin')
        response = self.client.get(reverse('manager:workout:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 200)
