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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
from collections import namedtuple

# Third Party
from actstream.models import Action
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.exercises.models import (
    Alias,
    Exercise,
    ExerciseComment,
    Translation,
)
from wger.exercises.views.helper import StreamVerbs


class SearchSubmissionApiTestCase(BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/exercise-submission/'

    @staticmethod
    def get_payload():
        return {
            'category': 3,
            'license': 5,
            'muscles': [3, 4],
            'muscles_secondary': [1],
            'equipment': [3],
            'license_author': 'test man',
            'variation_group': 'a1b2c3d4-0001-0000-0000-000000000001',
            'translations': [
                {
                    'name': '1-Arm Half-Kneeling Lat Pulldown',
                    'description_source': 'Attach a D-Handle to a high pully. And use your lat muscles to pull the weight single handedly.',
                    'language': 2,
                    'license_author': 'tester',
                    'aliases': [
                        {'alias': 'This is another name'},
                        {'alias': 'yet another name'},
                    ],
                    'comments': [
                        {'comment': 'This is a very important note about the exercise'},
                        {'comment': 'Do the exercise correctly and keep your back straight'},
                        {'comment': 'Remember to breathe out during the exertion phase'},
                    ],
                },
                {
                    'name': '2 Handed Kettlebell Swing',
                    'description_source': 'das ist die Beschreibung für die Übung',
                    'language': 1,
                    'license_author': 'tester',
                },
            ],
        }

    @staticmethod
    def get_counts():
        Counts = namedtuple('Counts', ['exercise', 'translation', 'alias', 'comment'])

        return Counts(
            Exercise.objects.count(),
            Translation.objects.count(),
            Alias.objects.count(),
            ExerciseComment.objects.count(),
        )

    def test_successful_submission_full(self):
        """Test that all objects were correctly created."""

        self.authenticate('admin')

        before = self.get_counts()
        response = self.client.post(self.url, data=self.get_payload())
        after = self.get_counts()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        exercise = Exercise.objects.get(pk=response.json().get('id'))

        self.assertEqual(exercise.category_id, 3)
        self.assertEqual(list(exercise.muscles.values_list('id', flat=True)), [3, 4])
        self.assertEqual(list(exercise.muscles_secondary.values_list('id', flat=True)), [1])
        self.assertEqual(list(exercise.equipment.values_list('id', flat=True)), [3])
        self.assertEqual(exercise.license_author, 'test man')
        self.assertEqual(str(exercise.variation_group), 'a1b2c3d4-0001-0000-0000-000000000001')

        self.assertEqual(before.exercise + 1, after.exercise)
        self.assertEqual(before.translation + 2, after.translation)
        self.assertEqual(before.alias + 2, after.alias)
        self.assertEqual(before.comment + 3, after.comment)

    def test_successful_submission_not_all_fields(self):
        """Test that all objects were correctly created even if not all fields are present."""

        self.authenticate('admin')

        payload = self.get_payload()
        payload['muscles_secondary'] = []
        payload['muscles'] = []
        payload['equipment'] = []
        payload['variation_group'] = None

        before = self.get_counts()
        response_data = self.client.post(self.url, data=payload).json()
        after = self.get_counts()
        print(response_data)
        exercise = Exercise.objects.get(pk=response_data.get('id'))

        self.assertEqual(exercise.category_id, 3)
        self.assertEqual(list(exercise.muscles.values_list('id', flat=True)), [])
        self.assertEqual(list(exercise.muscles_secondary.values_list('id', flat=True)), [])
        self.assertEqual(list(exercise.equipment.values_list('id', flat=True)), [])
        self.assertEqual(exercise.license_author, 'test man')
        self.assertIsNone(exercise.variation_group)

        self.assertEqual(before.exercise + 1, after.exercise)
        self.assertEqual(before.translation + 2, after.translation)
        self.assertEqual(before.alias + 2, after.alias)
        self.assertEqual(before.comment + 3, after.comment)

    def test_unsuccessful_submission_no_translations(self):
        """
        If any part of the exercise submission fails, no exercise is created.
        """
        self.authenticate('admin')

        payload = self.get_payload()
        payload['translations'] = []

        counts_before = self.get_counts()
        response = self.client.post(self.url, data=payload)
        response_data = response.json()
        counts_after = self.get_counts()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(counts_before, counts_after)
        self.assertEqual(
            response_data.get('translations'), ['You must provide at least one translation.']
        )

    def test_unsuccessful_submission_language_mismatch_description(self):
        """
        A translation whose description language doesn't match the declared language
        field is rejected.
        """
        self.authenticate('admin')

        payload = self.get_payload()
        # Swap the EN description for a clearly German one.
        payload['translations'][0]['description_source'] = (
            'Das ist eine deutsche Beschreibung der Übung, mit ausreichend Text '
            'damit die Spracherkennung sie zuverlässig erkennen kann.'
        )

        counts_before = self.get_counts()
        response = self.client.post(self.url, data=payload)
        counts_after = self.get_counts()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(counts_before, counts_after)
        self.assertIn('language', response.json().get('translations')[0])

    def test_unsuccessful_submission_language_mismatch_comment(self):
        """
        A comment whose detected language doesn't match the parent translation's
        language is rejected.
        """
        self.authenticate('admin')

        payload = self.get_payload()
        # Replace one of the English comments with a clearly French one.
        payload['translations'][0]['comments'][0]['comment'] = (
            'Ceci est un long commentaire en français qui ne correspond pas du '
            'tout à la traduction anglaise et devrait être rejeté.'
        )

        counts_before = self.get_counts()
        response = self.client.post(self.url, data=payload)
        counts_after = self.get_counts()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(counts_before, counts_after)

    def test_unsuccessful_submission_no_english_translations(self):
        """
        If any part of the exercise submission fails, no exercise is created.

        -> An exercise must have at least one English translation.
        """
        self.authenticate('admin')

        payload = self.get_payload()
        del payload['translations'][0]

        counts_before = self.get_counts()
        response = self.client.post(self.url, data=payload)
        response_data = response.json()
        counts_after = self.get_counts()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(counts_before, counts_after)
        self.assertEqual(
            response_data.get('translations'),
            ['You must provide at least one translation in English.'],
        )

    def test_submission_creates_actstream_events(self):
        """
        Every object created via the submission API produces a CREATED actstream event
        """

        self.authenticate('admin')

        actions_before = Action.objects.filter(verb=StreamVerbs.CREATED.value).count()
        response = self.client.post(self.url, data=self.get_payload())
        actions_after = Action.objects.filter(verb=StreamVerbs.CREATED.value).count()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Payload has: 1 exercise + 2 translations + 2 aliases + 3 comments = 8
        self.assertEqual(actions_after - actions_before, 8)

    def test_successfully_creates_new_variation(self):
        """
        Correctly connects the new exercise to another exercise via a new variation.
        """
        self.authenticate('admin')

        payload = self.get_payload()
        payload['variations_connect_to'] = 5
        del payload['variation_group']

        connected_exercise = Exercise.objects.get(pk=5)
        self.assertIsNone(connected_exercise.variation_group)

        response = self.client.post(self.url, data=payload)
        exercise = Exercise.objects.get(pk=response.json().get('id'))
        connected_exercise.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(exercise.variation_group)
        self.assertEqual(exercise.variation_group, connected_exercise.variation_group)
