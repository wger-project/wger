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
from decimal import Decimal

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.dataclasses import SetConfigData
from wger.manager.models import (
    RepsConfig,
    RestConfig,
    RiRConfig,
    WeightConfig,
    WorkoutLog,
)
from wger.manager.models.abstract_config import (
    OperationChoices,
    StepChoices,
)
from wger.manager.models.set_config import SetConfig


class SetConfigTestCase(WgerTestCase):
    """
    Test the set config calculations
    """

    set_config: SetConfig

    def setUp(self):
        super().setUp()
        self.set_config = SetConfig(set_id=1, exercise_id=1, order=1)
        self.set_config.save()

    def test_weight_config(self):
        """
        Test that the weight is correctly calculated for each step / iteration
        """

        # Initial value
        WeightConfig(set_config=self.set_config, iteration=1, value=80).save()

        # Increase by 2.5
        WeightConfig(set_config=self.set_config, iteration=3, value=2.5).save()

        # Replace with 42
        WeightConfig(set_config=self.set_config, iteration=6, value=42, replace=True).save()

        # Reduce by 2
        WeightConfig(
            set_config=self.set_config, iteration=7, value=2, operation=OperationChoices.MINUS
        ).save()

        # Increase by 10%
        WeightConfig(
            set_config=self.set_config,
            iteration=8,
            value=10,
            operation=OperationChoices.PLUS,
            step=StepChoices.PERCENT,
        ).save()

        self.assertEqual(self.set_config.get_weight(1), 80)
        self.assertEqual(self.set_config.get_weight(2), 80)
        self.assertEqual(self.set_config.get_weight(3), 82.5)
        self.assertEqual(self.set_config.get_weight(4), 82.5)
        self.assertEqual(self.set_config.get_weight(5), 82.5)
        self.assertEqual(self.set_config.get_weight(6), 42)
        self.assertEqual(self.set_config.get_weight(7), 40)
        self.assertEqual(self.set_config.get_weight(8), 44)

    def test_weight_config_with_logs(self):
        """
        Test that the weight is correctly calculated for each step / iteration
        if there are logs
        """

        # Initial value
        WeightConfig(set_config=self.set_config, iteration=1, value=80).save()
        RepsConfig(set_config=self.set_config, iteration=1, value=5).save()
        RestConfig(set_config=self.set_config, iteration=1, value=120).save()
        RiRConfig(set_config=self.set_config, iteration=1, value=2).save()

        # Increase weight by 2.5 at iteration 2
        WeightConfig(
            set_config=self.set_config,
            iteration=2,
            value=2.5,
            need_log_to_apply=True,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
        ).save()

        # Replace weight with 42 at iteration 5, no logs needed
        WeightConfig(
            set_config=self.set_config,
            iteration=5,
            value=42,
            replace=True,
            need_log_to_apply=False,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
        ).save()

        # Only did 4x82.5 at iteration 2
        WorkoutLog(
            exercise_base_id=1,
            user_id=1,
            workout_id=1,
            set_config=self.set_config,
            iteration=2,
            weight=82.5,
            reps=4,
        ).save()

        # Did 5x82.5 at iteration 3
        WorkoutLog(
            exercise_base_id=1,
            user_id=1,
            workout_id=1,
            set_config=self.set_config,
            iteration=3,
            weight=82.5,
            reps=5,
        ).save()

        self.assertEqual(
            self.set_config.get_config(1),
            SetConfigData(weight=80, reps=5, rir=2, rest=120),
        )
        self.assertEqual(
            self.set_config.get_config(2),
            SetConfigData(weight=80, reps=5, rir=2, rest=120),
        )
        self.assertEqual(
            self.set_config.get_config(3),
            SetConfigData(weight=80, reps=5, rir=2, rest=120),
        )
        self.assertEqual(
            self.set_config.get_config(4),
            SetConfigData(weight=Decimal(82.5), reps=5, rir=2, rest=120),
        )
        self.assertEqual(
            self.set_config.get_config(5),
            SetConfigData(weight=42, reps=5, rir=2, rest=120),
        )
        self.assertEqual(
            self.set_config.get_config(6),
            SetConfigData(weight=42, reps=5, rir=2, rest=120),
        )

    def test_weight_config_custom_python_class(self):
        """
        Test that the weight is correctly calculated for each step / iteration
        if there is custom python code defined
        """

        # Initial value with custom python code
        self.set_config.class_name = 'dummy'
        self.set_config.save()
        WeightConfig(set_config=self.set_config, iteration=1, value=100, replace=True).save()
        RepsConfig(set_config=self.set_config, iteration=1, value=5).save()
        RestConfig(set_config=self.set_config, iteration=1, value=120).save()
        RiRConfig(set_config=self.set_config, iteration=1, value=2).save()

        self.assertEqual(
            self.set_config.get_config(1),
            SetConfigData(weight=24, reps=1, rir=2, rest=120),
        )
        self.assertEqual(
            self.set_config.get_config(2),
            SetConfigData(weight=42, reps=10, rir=1, rest=90),
        )
        self.assertEqual(
            self.set_config.get_config(3),
            SetConfigData(weight=42, reps=10, rir=1, rest=90),
        )
