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
from wger.core.tests.api_base_test import ExerciseCrudApiTestCase
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import ExerciseComment
from wger.exercises.tests.api_mixins import ActstreamApiMixin


class ExerciseCommentRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(str(ExerciseComment.objects.get(pk=1)), 'test 123')


class ExerciseCommentApiTestCase(ActstreamApiMixin, ExerciseCrudApiTestCase):
    """
    Tests the exercise comment overview resource
    """

    pk = 1
    resource = ExerciseComment
    data = {
        'comment': 'This is a clearly English comment used for testing purposes.',
        'translation': '1',
        'id': 1,
    }

    def test_post_rejects_language_mismatch(self):
        """
        Adding a comment whose language doesn't match the parent translation's
        language is rejected.
        """

        # Translation pk=1 has language=2 (en); posting a German comment must
        # be rejected.
        self.authenticate('trainer1')
        response = self.client.post(
            self.url,
            data={
                'translation': 1,
                'comment': (
                    'Ein ausreichend langer deutscher Kommentar, damit die '
                    'Spracherkennung greifen kann und ihn ablehnt.'
                ),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('language', response.json())
