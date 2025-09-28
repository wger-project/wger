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
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.exercises.models import (
    Alias,
    Exercise,
    ExerciseComment,
    Translation,
    Variation,
)


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
            'variations': 1,
            'translations': [
                {
                    'name': '1-Arm Half-Kneeling Lat Pulldown',
                    'description': 'Attach a D-Handle to a high pully. And use your lat muscles to pull the weight single handedly.',
                    'language': 2,
                    'license_author': 'tester',
                    'aliases': [
                        {'alias': 'This is another name'},
                        {'alias': 'yet another name'},
                    ],
                    'comments': [
                        {'comment': 'This is a very important note'},
                        {'comment': 'Do the exercise correctly'},
                        {'comment': 'the third comment'},
                    ],
                },
                {
                    'name': '2 Handed Kettlebell Swing',
                    'description': '<p>das ist die Beschreibung für die Übung</p>',
                    'language': 1,
                    'license_author': 'tester',
                },
            ],
        }

    @staticmethod
    def get_counts():
        Counts = namedtuple('Counts', ['exercise', 'translation', 'alias', 'comment', 'variations'])

        return Counts(
            Exercise.objects.count(),
            Translation.objects.count(),
            Alias.objects.count(),
            ExerciseComment.objects.count(),
            Variation.objects.count(),
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
        self.assertEqual(exercise.variations_id, 1)

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
        payload['variations'] = None

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
        self.assertEqual(exercise.variations_id, None)

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

    def test_successfully_creates_new_variation(self):
        """
        Correctly connects the new exercise to another exercise via a new variation.
        """
        self.authenticate('admin')

        payload = self.get_payload()
        payload['variations_connect_to'] = 5
        del payload['variations']

        connected_exercise = Exercise.objects.get(pk=5)
        self.assertIsNone(connected_exercise.variations_id)

        counts_before = self.get_counts()
        response = self.client.post(self.url, data=payload)
        exercise = Exercise.objects.get(pk=response.json().get('id'))
        connected_exercise.refresh_from_db()
        counts_after = self.get_counts()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(counts_before.variations + 1, counts_after.variations)
        self.assertEqual(exercise.variations_id, connected_exercise.variations_id)
