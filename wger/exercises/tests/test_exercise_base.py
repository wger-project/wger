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

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import Exercise


class ExerciseBaseTestCase(WgerTestCase):
    """
    Test the different features of an exercise and its base
    """

    @staticmethod
    def get_ids(queryset):
        """Helper to return the IDs of the objects in a queryset"""
        return sorted([i.id for i in queryset.all()])

    def test_base(self):
        """
        Test that the properties return the correct data
        """
        exercise = Exercise.objects.get(pk=1)
        base = exercise.exercise_base
        self. assertEqual(base.category, exercise.category)
        self. assertListEqual(self.get_ids(base.equipment), self.get_ids(exercise.equipment))
        self. assertListEqual(self.get_ids(base.muscles), self.get_ids(exercise.muscles))
        self. assertListEqual(self.get_ids(base.muscles_secondary),
                              self.get_ids(exercise.muscles_secondary))

    def test_variations(self):
        """Test that the variations are correctly returned"""

        # Even if these exercises have the same base, only the variations for
        # their respective languages are returned.
        exercise = Exercise.objects.get(pk=81)
        self.assertListEqual(sorted([i.id for i in exercise.variations]), sorted([3, 35, 81]))

        exercise2 = Exercise.objects.get(pk=84)
        self.assertEqual(sorted([i.id for i in exercise2.variations]), sorted([84, 91, 111, 126]))

    def test_images(self):
        """Test that the correct images are returned for the exercises"""
        exercise = Exercise.objects.get(pk=1)
        base = exercise.exercise_base
        self.assertListEqual(self.get_ids(exercise.images), self.get_ids(base.exerciseimage_set))
