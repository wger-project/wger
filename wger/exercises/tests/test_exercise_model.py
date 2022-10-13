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


class ExerciseModelTestCase(WgerTestCase):
    """
    Test the logic in the exercise model
    """

    def test_absolute_url_name(self):
        """Test that the get_absolute_url returns the correct URL"""
        exercise = Exercise(exercise_base_id=1, description='abc', name='foo')
        self.assertEqual(exercise.get_absolute_url(), '/en/exercise/1/view-base/foo')

    def test_absolute_url_no_name(self):
        """Test that the get_absolute_url returns the correct URL"""
        exercise = Exercise(exercise_base_id=2, description='abc', name='')
        self.assertEqual(exercise.get_absolute_url(), '/en/exercise/2/view-base')

    def test_absolute_url_no_name2(self):
        """Test that the get_absolute_url returns the correct URL"""
        exercise = Exercise(exercise_base_id=42, description='abc', name='@@@@@')
        self.assertEqual(exercise.get_absolute_url(), '/en/exercise/42/view-base')
