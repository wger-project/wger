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
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.consts import (
    REP_UNIT_REPETITIONS,
    WEIGHT_UNIT_KG,
    WEIGHT_UNIT_LB,
)
from wger.manager.dataclasses import LogData
from wger.manager.models import WorkoutLog
from wger.manager.models.routine import Routine


class RoutineStatisticsTestCase(WgerTestCase):
    """
    Test the statistics calculations
    """

    routine: Routine

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

        # Exercise 1, 5 x 10kg, volume 50
        WorkoutLog(
            user_id=1,
            routine=self.routine,
            date=datetime.date(2024, 2, 1),
            repetitions_unit_id=REP_UNIT_REPETITIONS,
            repetitions=5,
            weight_unit_id=WEIGHT_UNIT_KG,
            weight=10,
            exercise_id=1,
            iteration=1,
        ).save()

        #  Exercise 1, 1 x 10kg, different day but same week, volume 10
        WorkoutLog(
            user_id=1,
            routine=self.routine,
            date=datetime.date(2024, 2, 2),
            repetitions_unit_id=REP_UNIT_REPETITIONS,
            repetitions=1,
            weight_unit_id=WEIGHT_UNIT_KG,
            weight=10,
            exercise_id=1,
            iteration=2,
        ).save()

        #  Exercise 3, 5 x 5kg, different week, volume 10
        WorkoutLog(
            user_id=1,
            routine=self.routine,
            date=datetime.date(2024, 2, 10),
            repetitions_unit_id=REP_UNIT_REPETITIONS,
            repetitions=1,
            weight_unit_id=WEIGHT_UNIT_KG,
            weight=10,
            exercise_id=3,
            iteration=3,
        ).save()

        #  Exercise 3, 5 x 5kg, different week, weight in lb
        WorkoutLog(
            user_id=1,
            routine=self.routine,
            date=datetime.date(2024, 2, 10),
            repetitions_unit_id=REP_UNIT_REPETITIONS,
            repetitions=1,
            weight_unit_id=WEIGHT_UNIT_LB,
            weight=10,
            exercise_id=3,
            iteration=3,
        ).save()

    def test_sets_calculations(self):
        stats = self.routine.calculate_log_statistics()

        # Mesocycle
        self.assertEqual(
            stats.sets.mesocycle,
            LogData(
                exercises={1: 2, 3: 1},
                muscle={1: 3, 2: 2},
                upper_body=0,
                lower_body=0,
                total=3,
            ),
        )

        # Iteration
        self.assertEqual(
            stats.sets.iteration[1],
            LogData(
                exercises={1: 1},
                muscle={1: 1, 2: 1},
                upper_body=0,
                lower_body=0,
                total=1,
            ),
        )
        self.assertEqual(
            stats.sets.iteration[2],
            LogData(
                exercises={1: 1},
                muscle={1: 1, 2: 1},
                upper_body=0,
                lower_body=0,
                total=1,
            ),
        )
        self.assertEqual(
            stats.sets.iteration[3],
            LogData(
                exercises={3: 1},
                muscle={1: 1},
                upper_body=0,
                lower_body=0,
                total=1,
            ),
        )

        # Weekly
        self.assertEqual(
            stats.sets.weekly[5],
            LogData(
                exercises={1: 2},
                muscle={1: 2, 2: 2},
                upper_body=0,
                lower_body=0,
                total=2,
            ),
        )
        self.assertEqual(
            stats.sets.weekly[6],
            LogData(
                exercises={3: 1},
                muscle={1: 1},
                upper_body=0,
                lower_body=0,
                total=1,
            ),
        )

        # Daily
        self.assertEqual(
            stats.sets.daily[datetime.date(2024, 2, 1)],
            LogData(
                exercises={1: 1},
                muscle={1: 1, 2: 1},
                upper_body=0,
                lower_body=0,
                total=1,
            ),
        )
        self.assertEqual(
            stats.sets.daily[datetime.date(2024, 2, 2)],
            LogData(
                exercises={1: 1},
                muscle={1: 1, 2: 1},
                upper_body=0,
                lower_body=0,
                total=1,
            ),
        )
        self.assertEqual(
            stats.sets.daily[datetime.date(2024, 2, 10)],
            LogData(
                exercises={3: 1},
                muscle={1: 1},
                upper_body=0,
                lower_body=0,
                total=1,
            ),
        )

    def test_volume_calculations(self):
        stats = self.routine.calculate_log_statistics()

        # Mesocycle
        self.assertEqual(
            stats.volume.mesocycle,
            LogData(
                exercises={1: 60, 3: 10},
                muscle={1: 70, 2: 60},
                upper_body=0,
                lower_body=0,
                total=70,
            ),
        )

        # Iteration
        self.assertEqual(
            stats.volume.iteration[1],
            LogData(
                exercises={1: 50},
                muscle={1: 50, 2: 50},
                upper_body=0,
                lower_body=0,
                total=50,
            ),
        )
        self.assertEqual(
            stats.volume.iteration[2],
            LogData(
                exercises={1: 10},
                muscle={1: 10, 2: 10},
                upper_body=0,
                lower_body=0,
                total=10,
            ),
        )
        self.assertEqual(
            stats.volume.iteration[3],
            LogData(
                exercises={3: 10},
                muscle={1: 10},
                upper_body=0,
                lower_body=0,
                total=10,
            ),
        )

        # Weekly
        self.assertEqual(
            stats.volume.weekly[5],
            LogData(
                exercises={1: 60},
                muscle={1: 60, 2: 60},
                upper_body=0,
                lower_body=0,
                total=60,
            ),
        )
        self.assertEqual(
            stats.volume.weekly[6],
            LogData(
                exercises={3: 10},
                muscle={1: 10},
                upper_body=0,
                lower_body=0,
                total=10,
            ),
        )

        # Daily
        self.assertEqual(
            stats.volume.daily[datetime.date(2024, 2, 1)],
            LogData(
                exercises={1: 50},
                muscle={1: 50, 2: 50},
                upper_body=0,
                lower_body=0,
                total=50,
            ),
        )
        self.assertEqual(
            stats.volume.daily[datetime.date(2024, 2, 2)],
            LogData(
                exercises={1: 10},
                muscle={1: 10, 2: 10},
                upper_body=0,
                lower_body=0,
                total=10,
            ),
        )
        self.assertEqual(
            stats.volume.daily[datetime.date(2024, 2, 10)],
            LogData(
                exercises={3: 10},
                muscle={1: 10},
                upper_body=0,
                lower_body=0,
                total=10,
            ),
        )

    def test_handle_null_weight(self):
        WorkoutLog(
            user_id=1,
            routine=self.routine,
            date=datetime.date(2024, 2, 12),
            repetitions_unit_id=REP_UNIT_REPETITIONS,
            repetitions=5,
            weight_unit_id=WEIGHT_UNIT_KG,
            weight=None,
            exercise_id=1,
            iteration=1,
        ).save()

        # No exception happens
        self.routine.calculate_log_statistics()

    def test_handle_null_repetitions(self):
        WorkoutLog(
            user_id=1,
            routine=self.routine,
            date=datetime.date(2024, 2, 12),
            repetitions_unit_id=REP_UNIT_REPETITIONS,
            repetitions=None,
            weight_unit_id=WEIGHT_UNIT_KG,
            weight=4,
            exercise_id=1,
            iteration=1,
        ).save()

        # No exception happens
        self.routine.calculate_log_statistics()
