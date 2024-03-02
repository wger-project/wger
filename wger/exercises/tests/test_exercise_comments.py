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
from wger.core.tests.api_base_test import ExerciseCrudApiTestCase
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import ExerciseComment


class ExerciseCommentRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(str(ExerciseComment.objects.get(pk=1)), 'test 123')


class ExerciseCommentApiTestCase(ExerciseCrudApiTestCase):
    """
    Tests the exercise comment overview resource
    """

    pk = 1
    resource = ExerciseComment
    data = {
        'comment': 'a cool comment',
        'exercise': '1',
        'id': 1,
    }
