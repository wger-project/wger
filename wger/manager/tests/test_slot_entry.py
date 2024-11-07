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
    MaxRepsConfig,
    MaxWeightConfig,
    RepsConfig,
    RestConfig,
    RiRConfig,
    SetsConfig,
    SlotEntry,
    WeightConfig,
    WorkoutLog,
)
from wger.manager.models.abstract_config import (
    OperationChoices,
    StepChoices,
)


class SlotEntryTestCase(WgerTestCase):
    """
    Test the slot entry calculations
    """

    slot_entry: SlotEntry

    def setUp(self):
        super().setUp()

        self.slot_entry = SlotEntry(
            slot_id=1,
            exercise_id=1,
            order=1,
        )
        self.slot_entry.save()

    def test_weight_config(self):
        """
        Test that the weight is correctly calculated for each step / iteration
        """

        # Initial value
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=80,
            operation=OperationChoices.REPLACE,
        ).save()

        # Increase by 2.5
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=3,
            value=2.5,
            operation=OperationChoices.PLUS,
        ).save()

        # Replace with 42
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=6,
            value=42,
            operation=OperationChoices.REPLACE,
        ).save()

        # Reduce by 2
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=7,
            value=2,
            operation=OperationChoices.MINUS,
        ).save()

        # Increase by 10%
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=8,
            value=10,
            operation=OperationChoices.PLUS,
            step=StepChoices.PERCENT,
        ).save()

        self.assertEqual(self.slot_entry.get_weight(1), 80)
        self.assertEqual(self.slot_entry.get_weight(2), 80)
        self.assertEqual(self.slot_entry.get_weight(3), 82.5)
        self.assertEqual(self.slot_entry.get_weight(4), 82.5)
        self.assertEqual(self.slot_entry.get_weight(5), 82.5)
        self.assertEqual(self.slot_entry.get_weight(6), 42)
        self.assertEqual(self.slot_entry.get_weight(7), 40)
        self.assertEqual(self.slot_entry.get_weight(8), 44)

    def test_weight_config_with_logs(self):
        """
        Test that the weight is correctly calculated for each step / iteration
        if there are logs
        """

        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.repetition_rounding = 2
        self.slot_entry.save()

        # Initial value
        SetsConfig(slot_entry=self.slot_entry, iteration=1, value=4).save()
        RepsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        RestConfig(slot_entry=self.slot_entry, iteration=1, value=120).save()
        RiRConfig(slot_entry=self.slot_entry, iteration=1, value=2).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=80,
        ).save()

        # Increase weight by 2.5 at iteration 2
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=2.5,
            need_log_to_apply=True,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
        ).save()

        # Replace weight with 42 at iteration 5, no logs needed
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=5,
            value=42,
            need_log_to_apply=False,
            operation=OperationChoices.REPLACE,
            step=StepChoices.ABSOLUTE,
        ).save()

        # Only did 4x82.5 at iteration 2
        WorkoutLog(
            exercise_id=1,
            user_id=1,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=2,
            weight=82.5,
            reps=4,
        ).save()

        # Did 5x82.5 at iteration 3
        WorkoutLog(
            exercise_id=1,
            user_id=1,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=3,
            weight=82.5,
            reps=5,
        ).save()

        self.assertEqual(
            self.slot_entry.get_config(1),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=4,
                weight=80,
                weight_rounding=Decimal('2.5'),
                reps=5,
                reps_rounding=2,
                rir=2,
                rest=120,
            ),
        )

        self.assertEqual(
            self.slot_entry.get_config(2),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=4,
                weight=80,
                weight_rounding=Decimal('2.5'),
                reps=5,
                reps_rounding=2,
                rir=2,
                rest=120,
            ),
        )

        self.assertEqual(
            self.slot_entry.get_config(3),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=4,
                weight=80,
                weight_rounding=Decimal('2.5'),
                reps=5,
                reps_rounding=2,
                rir=2,
                rest=120,
            ),
        )

        self.assertEqual(
            self.slot_entry.get_config(4),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=4,
                weight=Decimal(82.5),
                weight_rounding=Decimal('2.5'),
                reps=5,
                reps_rounding=2,
                rir=2,
                rest=120,
            ),
        )

        self.assertEqual(
            self.slot_entry.get_config(5),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=4,
                weight=42,
                weight_rounding=Decimal('2.5'),
                reps=5,
                reps_rounding=2,
                rir=2,
                rest=120,
            ),
        )

        self.assertEqual(
            self.slot_entry.get_config(6),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=4,
                weight=42,
                weight_rounding=Decimal('2.5'),
                reps=5,
                reps_rounding=2,
                rir=2,
                rest=120,
            ),
        )

    def test_weight_config_with_logs_and_range(self):
        """
        Test that the weight is correctly calculated for each step / iteration
        if there are logs and there is a weight / rep range
        """

        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.repetition_rounding = 2
        self.slot_entry.save()

        # Initial value: 5-6 reps x 80-100 kg
        RepsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        MaxRepsConfig(slot_entry=self.slot_entry, iteration=1, value=6).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=80,
        ).save()

        MaxWeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=100,
        ).save()

        # Only did 4x82.5 at iteration 2
        WorkoutLog(
            exercise_id=1,
            user_id=1,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=2,
            weight=82.5,
            reps=4,
        ).save()

        # 5x80 at iteration 3
        WorkoutLog(
            exercise_id=1,
            user_id=1,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=3,
            weight=80,
            reps=5,
        ).save()

        self.assertEqual(
            self.slot_entry.get_config(1),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=1,
                weight=80,
                max_weight=100,
                weight_rounding=Decimal('2.5'),
                reps=5,
                max_reps=6,
                reps_rounding=2,
                rir=None,
                rest=None,
            ),
        )

        self.assertEqual(
            self.slot_entry.get_config(2),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=1,
                weight=80,
                max_weight=100,
                weight_rounding=Decimal('2.5'),
                reps=5,
                max_reps=6,
                reps_rounding=2,
                rir=None,
                rest=None,
            ),
        )

    def test_weight_config_custom_python_class(self):
        """
        Test that the weight is correctly calculated for each step / iteration
        if there is custom python code defined
        """

        # Initial value with custom python code
        self.slot_entry.class_name = 'dummy'
        self.slot_entry.save()
        SetsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=100,
            operation=OperationChoices.REPLACE,
        ).save()
        RepsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        RestConfig(slot_entry=self.slot_entry, iteration=1, value=120).save()
        RiRConfig(slot_entry=self.slot_entry, iteration=1, value=2).save()

        self.assertEqual(
            self.slot_entry.get_config(1),
            SetConfigData(exercise=1, sets=2, weight=24, reps=1, rir=2, rest=120),
        )
        self.assertEqual(
            self.slot_entry.get_config(2),
            SetConfigData(exercise=2, sets=4, weight=42, reps=10, rir=1, rest=90),
        )
        self.assertEqual(
            self.slot_entry.get_config(3),
            SetConfigData(exercise=2, sets=4, weight=42, reps=10, rir=1, rest=90),
        )

    def test_empty_configs(self):
        """
        Test that the correct config is calculated if there are no configs at all
        """

        print(self.slot_entry.get_config(1))
        self.assertEqual(
            self.slot_entry.get_config(1),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=1,
                weight=None,
                weight_rounding=None,
                weight_unit=None,
                reps=None,
                reps_rounding=None,
                reps_unit=None,
                rir=None,
                rest=None,
            ),
        )
