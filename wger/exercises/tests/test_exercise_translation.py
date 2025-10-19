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
import json

# Django
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests import api_base_test
from wger.core.tests.api_base_test import ExerciseCrudApiTestCase
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    Exercise,
    Muscle,
    Translation,
)
from wger.utils.constants import (
    CC_0_LICENSE_ID,
    CC_BY_SA_4_LICENSE_ID,
)


class ExerciseRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(str(Translation.objects.get(pk=1)), 'An exercise')


class ExercisesTestCase(WgerTestCase):
    """
    Exercise test case
    """

    def search_exercise(self, fail=True):
        """
        Helper function to test searching for exercises
        """

        # 1 hit, "Very cool exercise"
        response = self.client.get(reverse('exercise-search'), {'term': 'cool'})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result), 1)
        self.assertEqual(result['suggestions'][0]['value'], 'Very cool exercise')
        self.assertEqual(result['suggestions'][0]['data']['id'], 2)
        self.assertEqual(result['suggestions'][0]['data']['category'], 'Another category')
        self.assertEqual(result['suggestions'][0]['data']['image'], None)
        self.assertEqual(result['suggestions'][0]['data']['image_thumbnail'], None)

        # 0 hits, "Pending exercise"
        response = self.client.get(reverse('exercise-search'), {'term': 'Foobar'})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result['suggestions']), 0)

    def test_search_exercise_anonymous(self):
        """
        Test deleting an exercise by an anonymous user
        """

        self.search_exercise()

    def test_search_exercise_logged_in(self):
        """
        Test deleting an exercise by a logged-in user
        """

        self.user_login('test')
        self.search_exercise()

    def test_exercise_records_historical_data(self):
        """
        Test that changing exercise details generates a historical record
        """
        translation = Translation.objects.get(pk=2)
        self.assertEqual(len(translation.history.all()), 0)

        translation.name = 'Very cool exercise 2'
        translation.description = 'New description'
        translation.exercise.muscles_secondary.add(Muscle.objects.get(pk=2))
        translation.save()

        translation = Translation.objects.get(pk=2)
        self.assertEqual(len(translation.history.all()), 1)


# TODO: fix test, all registered users can upload exercises
class ExerciseApiTestCase(
    api_base_test.BaseTestCase, api_base_test.ApiBaseTestCase, api_base_test.ApiGetTestCase
):
    """
    Tests the exercise overview resource
    """

    pk = 1
    resource = Exercise
    private_resource = False
    overview_cached = False

    def get_resource_name(self):
        return 'exercise'


# TODO: fix test, all registered users can upload exercises
class ExerciseTranslationApiTestCase(
    api_base_test.BaseTestCase, api_base_test.ApiBaseTestCase, api_base_test.ApiGetTestCase
):
    """
    Tests the exercise overview resource
    """

    pk = 1
    resource = Translation
    private_resource = False
    overview_cached = False

    def get_resource_name(self):
        return 'exercise-translation'


class ExerciseInfoApiTestCase(
    api_base_test.BaseTestCase,
    api_base_test.ApiBaseTestCase,
    api_base_test.ApiGetTestCase,
):
    """
    Tests the exercise base info resource
    """

    pk = 1
    private_resource = False
    overview_cached = True

    def get_resource_name(self):
        return 'exerciseinfo'


class ExerciseTranslationCustomApiTestCase(ExerciseCrudApiTestCase):
    pk = 1

    data = {
        'name': 'A new name',
        'description': 'The wild boar is a suid native to much of Eurasia and North Africa',
        'language': 1,
        'exercise': 1,
    }

    def get_resource_name(self):
        return 'exercise-translation'

    def test_cant_change_exercise_id(self):
        """
        Test that it is not possible to change the exercise id of an existing
        translation.
        """
        Translation.objects.filter(exercise_id=2).delete()
        translation = Translation.objects.get(pk=self.pk)
        self.assertEqual(translation.exercise_id, 1)

        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'exercise': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        translation = Translation.objects.get(pk=self.pk)
        self.assertEqual(translation.exercise_id, 1)

    def test_cant_change_language(self):
        """
        Test that it is not possible to change the language id of an existing
        exercise translation.
        """
        translation = Translation.objects.get(pk=self.pk)
        self.assertEqual(translation.language_id, 2)

        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'language': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        translation = Translation.objects.get(pk=self.pk)
        self.assertEqual(translation.language_id, 2)

    def test_cant_change_license(self):
        """
        Test that it is not possible to change the license of an existing
        exercise translation.
        """
        translation = Translation.objects.get(pk=self.pk)
        self.assertEqual(translation.license_id, 2)

        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'license': 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        translation = Translation.objects.get(pk=self.pk)
        self.assertEqual(translation.license_id, 2)

    def test_cant_set_license(self):
        """
        Test that it is not possible to set the license for a newly created
        exercise translation (the license is always set to the default)
        """
        self.data['license'] = CC_0_LICENSE_ID

        self.authenticate('trainer1')
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        translation = Translation.objects.get(pk=self.pk)
        self.assertEqual(translation.license_id, CC_BY_SA_4_LICENSE_ID)

    def test_patch_clean_html(self):
        """
        Test that the description field has its HTML stripped before saving
        """
        description = '<script>alert();</script> The wild boar is a suid native...'
        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'description': description})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        translation = Translation.objects.get(pk=self.pk)
        self.assertEqual(translation.description, 'alert(); The wild boar is a suid native...')

    def test_post_only_one_language_per_base(self):
        """
        Test that it's not possible to add a second translation for the same
        exercise in the same language.
        """
        self.authenticate('trainer1')
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, data=self.data)
        self.assertTrue(response.data['non_field_errors'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_existing_language(self):
        """
        Test that it is possible to set the language if it doesn't duplicate a translation
        """
        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'language': 1, 'name': '123456'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get('non_field_errors'))

    def test_edit_only_one_language_per_base(self):
        """
        Test that it's not possible to edit a translation to a second language for the same base
        """
        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'language': 3})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['non_field_errors'])
