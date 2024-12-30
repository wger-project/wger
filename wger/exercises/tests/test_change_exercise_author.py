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
from io import StringIO

# Django
from django.core.management import call_command

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models.base import ExerciseBase
from wger.exercises.models.exercise import Exercise


class ChangeExerciseAuthorTestCase(WgerTestCase):
    """
    Tests the change exercise author command
    """

    def setUp(self):
        super(ChangeExerciseAuthorTestCase, self).setUp()
        self.out = StringIO()

    def test_missing_author(self):
        """
        Test to ensure command handles a missing author parameter
        """
        call_command('change-exercise-author', stdout=self.out, no_color=True)
        self.assertIn('Please enter an author name', self.out.getvalue())

    def test_missing_exercise(self):
        """
        Test to ensure command handles a missing exercise parameters
        """
        args = ['--author-name', 'tom']
        call_command('change-exercise-author', *args, stdout=self.out, no_color=True)
        self.assertIn('Please enter an exercise base or exercise ID', self.out.getvalue())

    def test_can_update_exercise_base(self):
        """
        Test to ensure command can handle an exercise base id passed
        """
        exercise = ExerciseBase.objects.get(id=2)
        self.assertNotEqual(exercise.license_author, 'tom')

        args = ['--author-name', 'tom', '--exercise-base-id', '2']
        call_command('change-exercise-author', *args, stdout=self.out, no_color=True)
        self.assertIn('Exercise and/or exercise base has been updated', self.out.getvalue())

        exercise = ExerciseBase.objects.get(id=2)
        self.assertEqual(exercise.license_author, 'tom')

    def test_can_update_exercise(self):
        """
        Test to ensure command can handle an exercise id passed
        """
        exercise = Exercise.objects.get(id=1)
        self.assertNotEqual(exercise.license_author, 'tom')

        args = ['--author-name', 'tom', '--exercise-id', '1']
        call_command('change-exercise-author', *args, stdout=self.out, no_color=True)
        self.assertIn('Exercise and/or exercise base has been updated', self.out.getvalue())

        exercise = Exercise.objects.get(id=1)
        self.assertEqual(exercise.license_author, 'tom')
