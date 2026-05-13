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
from wger.exercises.tests.api_mixins import ActstreamApiMixin
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

        translation.refresh_from_db()
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


class ExerciseTranslationCustomApiTestCase(ActstreamApiMixin, ExerciseCrudApiTestCase):
    pk = 1
    resource = Translation

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

    def test_post_without_description_succeeds(self):
        """
        POSTing only with ``description_source`` must succeed.
        """
        payload = {
            'name': 'A new translation',
            'description_source': (
                'Beuge die Knie und gehe in die tiefe Hocke, halte dabei den '
                'Rücken gerade und die Brust aufrecht.'
            ),
            'language': 1,
            'exercise': 1,
        }
        Translation.objects.filter(exercise_id=1, language_id=1).delete()

        self.authenticate('trainer1')
        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        translation = Translation.objects.get(pk=response.json()['id'])
        self.assertEqual(translation.description_source, payload['description_source'])
        # Backend rendered the markdown into description on save()
        self.assertIn('Beuge die Knie', translation.description)

    def test_cant_set_description_directly(self):
        """
        ``description`` is read-only, passing it on POST must be silently
        dropped, not stored as raw HTML.
        """
        payload = {
            'name': 'A new translation',
            'description': '<script>alert(1)</script><p>raw html</p>',
            'description_source': (
                'Sicherer Markdown-Text der nur in deutscher Sprache geschrieben '
                'ist um die Spracherkennung zuverlässig zu bestehen.'
            ),
            'language': 1,
            'exercise': 1,
        }
        Translation.objects.filter(exercise_id=1, language_id=1).delete()

        self.authenticate('trainer1')
        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        translation = Translation.objects.get(pk=response.json()['id'])

        self.assertNotIn('<script>', translation.description)
        self.assertNotIn('raw html', translation.description)
        self.assertIn('Sicherer Markdown-Text', translation.description)

    def test_cant_patch_description_directly(self):
        """
        PATCHing ``description`` on an existing translation must not store the raw API input
        """
        self.authenticate('trainer1')
        response = self.client.patch(
            self.url_detail,
            data={'description': '<p>injected via API</p>'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        translation = Translation.objects.get(pk=self.pk)
        self.assertNotIn('injected via API', translation.description)

    def test_patch_clean_html(self):
        """
        Test that HTML in description_source is sanitized (script tags stripped) before saving
        """
        description = '<script>alert();</script> The wild boar is a suid native...'
        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'description_source': description})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        translation = Translation.objects.get(pk=self.pk)
        self.assertEqual(translation.description, ' The wild boar is a suid native...')

    def test_post_accepts_matching_language(self):
        """
        POSTing a translation whose description is in the declared language
        succeeds (positive counterpart to ``test_post_rejects_language_mismatch``).
        """
        Translation.objects.filter(exercise_id=1, language_id=1).delete()

        payload = {
            'name': 'Eine neue Übersetzung',
            'description_source': (
                'Halte die Hantel mit beiden Händen und führe die Bewegung '
                'kontrolliert aus, dabei den Rücken stets gerade.'
            ),
            'language': 1,
            'exercise': 1,
        }
        self.authenticate('trainer1')
        response = self.client.post(self.url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_rejects_language_mismatch(self):
        """
        POSTing a translation whose description language doesn't match the
        declared language field is rejected.
        """

        # Free up exercise=1/language=2 so the duplicate-translation check
        # doesn't fire before the language-mismatch check.
        Translation.objects.filter(exercise_id=1, language_id=2).delete()

        payload = {
            'name': 'A new translation',
            'description_source': (
                'Das ist eine deutsche Beschreibung der Übung, mit ausreichend '
                'Text damit die Spracherkennung sie zuverlässig erkennen kann.'
            ),
            'language': 2,
            'exercise': 1,
        }
        self.authenticate('trainer1')
        response = self.client.post(self.url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('language', response.json())

    def test_patch_rejects_language_mismatch(self):
        """
        PATCHing ``description_source`` to text in a different language than
        the (existing) translation's language is rejected.
        """

        # Translation pk=1 has language=2 (en); push a clearly German
        # description and expect the validator to reject it.
        self.authenticate('trainer1')
        response = self.client.patch(
            self.url_detail,
            data={
                'description_source': (
                    'Eine ausreichend lange deutsche Beschreibung, damit die '
                    'Spracherkennung sicher greifen kann.'
                ),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('language', response.json())

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
