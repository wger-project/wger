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
from uuid import UUID

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ExerciseCrudApiTestCase
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    DeletionLog,
    Exercise,
    ExerciseBase,
)
from wger.utils.constants import CC_BY_SA_4_ID


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
        translation = Exercise.objects.get(pk=1)
        exercise = translation.exercise_base
        self.assertEqual(exercise.category, translation.category)
        self.assertListEqual(self.get_ids(exercise.equipment), self.get_ids(translation.equipment))
        self.assertListEqual(self.get_ids(exercise.muscles), self.get_ids(translation.muscles))
        self.assertListEqual(
            self.get_ids(exercise.muscles_secondary),
            self.get_ids(translation.muscles_secondary),
        )

    def test_language_utils_translation_exists(self):
        """
        Test that the base correctly returns translated exercises
        """
        exercise = ExerciseBase.objects.get(pk=1).get_translation('de')
        self.assertEqual(exercise.name, 'An exercise')

    def test_language_utils_no_translation_exists(self):
        """
        Test that the base correctly returns the English translation if the
        requested language does not exist
        """
        exercise = ExerciseBase.objects.get(pk=1).get_translation('fr')
        self.assertEqual(exercise.name, 'Test exercise 123')

    def test_language_utils_no_translation_fallback(self):
        """
        Test that the base correctly returns the first translation if for whatever
        reason English is not available
        """
        exercise = ExerciseBase.objects.get(pk=2).get_translation('pt')

        self.assertEqual(exercise.name, 'Very cool exercise')

    def test_variations(self):
        """Test that the variations are correctly returned"""

        # Even if these exercises have the same base, only the variations for
        # their respective languages are returned.
        exercise = ExerciseBase.objects.get(pk=1)
        self.assertListEqual(sorted([i.id for i in exercise.base_variations]), [2])

        exercise2 = ExerciseBase.objects.get(pk=3)
        self.assertEqual(sorted([i.id for i in exercise2.base_variations]), [4])

    def test_images(self):
        """Test that the correct images are returned for the exercises"""
        translation = Exercise.objects.get(pk=1)
        exercise = translation.exercise_base
        self.assertListEqual(
            self.get_ids(translation.images), self.get_ids(exercise.exerciseimage_set)
        )


class ExerciseCustomApiTestCase(ExerciseCrudApiTestCase):
    pk = 1

    data = {
        'category': 3,
        'muscles': [1, 3],
        'muscles_secondary': [2],
        'equipment': [3],
        'variations': 4,
    }

    def get_resource_name(self):
        return 'exercise-base'

    def test_delete_replace_by(self):
        """Test that setting the replaced_by attribute works"""

        self.authenticate('admin')

        url = self.url_detail + '?replaced_by=ae3328ba-9a35-4731-bc23-5da50720c5aa'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        log = DeletionLog.objects.get(pk=1)

        self.assertEqual(log.model_type, 'base')
        self.assertEqual(log.uuid, UUID('acad3949-36fb-4481-9a72-be2ddae2bc05'))
        self.assertEqual(log.replaced_by, UUID('ae3328ba-9a35-4731-bc23-5da50720c5aa'))

    def test_cant_change_license(self):
        """
        Test that it is not possible to change the license of an existing
        exercise base
        """
        exercise = ExerciseBase.objects.get(pk=self.pk)
        self.assertEqual(exercise.license_id, 2)

        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'license': 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        exercise = ExerciseBase.objects.get(pk=self.pk)
        self.assertEqual(exercise.license_id, 2)

    def test_cant_set_license(self):
        """
        Test that it is not possible to set the license for a newly created
        exercise base (the license is always set to the default)
        """
        self.data['license'] = 3

        self.authenticate('trainer1')
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        exercise = ExerciseBase.objects.get(pk=self.pk)
        self.assertEqual(exercise.license_id, CC_BY_SA_4_ID)
