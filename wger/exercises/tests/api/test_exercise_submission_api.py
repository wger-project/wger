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

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.exercises.models import Exercise


class SearchSubmissionApiTestCase(BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/exercise-submission/'

    def test_successful_submission(self):
        self.authenticate('admin')

        payload = {
            'category': 3,
            'license': 5,
            'muscles': [3, 4],
            'muscles_secondary': [1],
            'equipment': [3],
            'license_author': 'test man',
            'variation': 1,
            'translations': [
                {
                    'name': '1-Arm Half-Kneeling Lat Pulldown',
                    'description': 'Attach a D-Handle to a high pully. And use your lat muscles to pull the weight single handedly.',
                    'language': 2,
                    'license_author': 'tester',
                    'aliases': [
                        {'alias': 'This is another name'},
                        {'alias': 'ashda dsads asa dssa'},
                    ],
                    'comments': [
                        {'comment': 'This is a very important note'},
                        {'comment': 'Do the exercise correctly'},
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

        count_before = Exercise.objects.count()
        response = self.client.post(self.url, data=payload)
        count_after = Exercise.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('id'), 9)
        self.assertEqual(count_before + 1, count_after)

    def test_unsuccessful_submission(self):
        """
        If any part of the exercise submission fails, no exercise is created.
        """
        self.authenticate('admin')

        payload = {
            'category': 100,
            'license': 5,
            'muscles': [3, 4],
            'muscles_secondary': [1],
            'equipment': [3],
            'license_author': 'test man',
            'variation': 1,
            'translations': [
                {
                    'name': '1-Arm Half-Kneeling Lat Pulldown',
                    'description': 'Attach a D-Handle to a high pully. And use your lat muscles to pull the weight single handedly.',
                    'language': 2,
                    'license_author': 'tester',
                    'aliases': [
                        {'alias': 'This is another name'},
                        {'alias': 'ashda dsads asa dssa'},
                    ],
                    'comments': [
                        {'comment': 'This is a very important note'},
                        {'comment': 'Do the exercise correctly'},
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

        count_before = Exercise.objects.count()
        response = self.client.post(self.url, data=payload)
        count_after = Exercise.objects.count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(count_before, count_after)
