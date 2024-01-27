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

# Django
from django.core.management import call_command

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import (
    Workout,
    WorkoutLog,
)


class RoutineGeneratorTestCase(WgerTestCase):
    def test_generator_routines(self):
        # Arrange
        Workout.objects.all().delete()

        # Act
        call_command('dummy-generator-workout-plans', '--plans', 10)

        # Assert
        self.assertEqual(Workout.objects.filter(user_id=1).count(), 10)

    def test_generator_diary_entries(self):
        # Arrange
        Workout.objects.all().delete()

        # Act
        call_command('dummy-generator-workout-plans', '--plans', 1)
        call_command('dummy-generator-workout-diary', '--diary-entries', 10)

        # Assert
        # Things like nr of training days or exercises are random
        min_entries = 1 * 1 * 3 * 3 * 10
        max_entries = 1 * 5 * 3 * 10 * 10
        self.assertGreaterEqual(WorkoutLog.objects.filter(workout__user_id=1).count(), min_entries)
        self.assertLessEqual(WorkoutLog.objects.filter(workout__user_id=1).count(), max_entries)
