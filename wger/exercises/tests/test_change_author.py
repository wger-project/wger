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

from io import StringIO

from django.core.management import call_command

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models.exercise import Exercise


class ChangeAuthorTestCase(WgerTestCase):
    """
    Tests the change author command
    """

    def setUp(self):
        super(ChangeAuthorTestCase, self).setUp()
        self.out = StringIO()


    def test_missing_author(self):
        """
        Test to ensure command handles a missing author parameter
        """
        call_command('change-author', stdout=self.out, no_color=True)
        self.assertIn('Please enter an author name', self.out.getvalue())

    def test_missing_exercise(self):
        """
        Test to ensure command handles a missing exercise parameters
        """
        args = [
            "--author-name",
            "tom"
        ]
        call_command('change-author', *args, stdout=self.out, no_color=True)
        self.assertIn('Please enter an exercise ID', self.out.getvalue())

    def test_can_update_exercise(self):
        """
        Test to ensure command can handle an exercise id passed
        """
        exercise = Exercise.objects.get(id=1)
        self.assertNotEquals(exercise.license_author, "tom")

        args = [
            "--author-name",
            "tom",
            "--exercise-id",
            "1"
        ]
        call_command('change-author', *args, stdout=self.out, no_color=True)
        self.assertIn('Exercise has been updated', self.out.getvalue())

        exercise = Exercise.objects.get(id=1)
        self.assertEquals(exercise.license_author, "tom")
