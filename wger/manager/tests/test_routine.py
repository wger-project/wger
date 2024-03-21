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
import datetime

# wger
from wger.core.tests.api_base_test import ApiBaseResourceTestCase
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.dataclasses import WorkoutDayData
from wger.manager.models import (
    DayNg,
    WorkoutSession,
)
from wger.manager.models.routine import Routine


class RoutineTestCase(WgerTestCase):
    """
    Test the different day and date functions
    """

    routine: Routine
    day1: DayNg
    day2: DayNg
    day3: DayNg

    def setUp(self):
        super().setUp()

        self.routine = Routine(
            user_id=1,
            name='A routine',
            description='A routine',
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
        )
        self.routine.save()

        self.day1 = DayNg(routine=self.routine, description='day 1')
        self.day1.save()

        self.day2 = DayNg(
            routine=self.routine,
            description='day 2',
            is_rest=True,
        )
        self.day2.save()

        self.day3 = DayNg(routine=self.routine, description='day 3')
        self.day3.save()

        self.day1.next_day = self.day2
        self.day1.save()

        self.day2.next_day = self.day3
        self.day2.save()

        self.day3.next_day = self.day1
        self.day3.save()

        self.routine.first_day = self.day1

    def test_day_sequences(self):
        self.assertListEqual(
            self.routine.day_sequence,
            [self.day1, self.day2, self.day3],
        )

    def test_date_sequences(self):
        """
        Test that the days are correctly outputted in a sequence
        """

        self.assertEqual(
            self.routine.date_sequence,
            {
                datetime.date(2024, 1, 1): WorkoutDayData(day=self.day1, iteration=1),
                datetime.date(2024, 1, 2): WorkoutDayData(day=self.day2, iteration=1),
                datetime.date(2024, 1, 3): WorkoutDayData(day=self.day3, iteration=1),
                datetime.date(2024, 1, 4): WorkoutDayData(day=self.day1, iteration=2),
                datetime.date(2024, 1, 5): WorkoutDayData(day=self.day2, iteration=2),
                datetime.date(2024, 1, 6): WorkoutDayData(day=self.day3, iteration=2),
                datetime.date(2024, 1, 7): WorkoutDayData(day=self.day1, iteration=3),
                datetime.date(2024, 1, 8): WorkoutDayData(day=self.day2, iteration=3),
                datetime.date(2024, 1, 9): WorkoutDayData(day=self.day3, iteration=3),
                datetime.date(2024, 1, 10): WorkoutDayData(day=self.day1, iteration=4),
            },
        )

    def test_date_sequences_logs(self):
        """
        Test that the days are correctly outputted in a sequence

        Day one needs logs to advance, till then it will be repeated
        """

        # Arrange
        self.day1.need_logs_to_advance = True
        self.day1.save()

        dates = [
            datetime.date(2024, 1, 4),
            datetime.date(2024, 1, 7),
        ]

        for date in dates:
            session = WorkoutSession(
                user_id=1,
                date=date,
                day=self.day1,
                workout_id=1,
            )
            session.save()

        # Assert
        self.assertEqual(
            self.routine.date_sequence,
            {
                datetime.date(2024, 1, 1): WorkoutDayData(day=self.day1, iteration=1),
                datetime.date(2024, 1, 2): WorkoutDayData(day=self.day1, iteration=2),
                datetime.date(2024, 1, 3): WorkoutDayData(day=self.day1, iteration=3),
                datetime.date(2024, 1, 4): WorkoutDayData(day=self.day1, iteration=4),
                datetime.date(2024, 1, 5): WorkoutDayData(day=self.day2, iteration=1),
                datetime.date(2024, 1, 6): WorkoutDayData(day=self.day3, iteration=1),
                datetime.date(2024, 1, 7): WorkoutDayData(day=self.day1, iteration=5),
                datetime.date(2024, 1, 8): WorkoutDayData(day=self.day2, iteration=2),
                datetime.date(2024, 1, 9): WorkoutDayData(day=self.day3, iteration=2),
                datetime.date(2024, 1, 10): WorkoutDayData(day=self.day1, iteration=6),
            },
        )


class RoutineApiTestCase(ApiBaseResourceTestCase):
    """
    Tests the routine api endpoint
    """

    pk = 1
    resource = Routine
    private_resource = True
    data = {
        'name': 'A new comment',
        'start': '2024-03-11',
        'end': '2024-06-20',
    }
