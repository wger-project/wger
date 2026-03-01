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
from dataclasses import asdict
from decimal import Decimal

# Django
from django.core.cache import cache
from django.test import SimpleTestCase

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.dataclasses import SetConfigData
from wger.manager.models import (
    MaxRepetitionsConfig,
    MaxWeightConfig,
    RepetitionsConfig,
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
from wger.utils.cache import CacheKeyMapper


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

    def test_auto_add_order(self):
        """
        Test that the order is automatically added if not provided
        """
        SlotEntry.objects.filter(slot_id=1).delete()

        slot_entry_1 = SlotEntry(slot_id=1, exercise_id=1)
        slot_entry_1.save()

        slot_entry_2 = SlotEntry(slot_id=1, exercise_id=2, order=None)
        slot_entry_2.save()

        slot_entry_3 = SlotEntry(slot_id=1, exercise_id=3, order=7)
        slot_entry_3.save()

        slot_entry_4 = SlotEntry(slot_id=1, exercise_id=3)
        slot_entry_4.save()

        self.assertEqual(slot_entry_1.order, 1)
        self.assertEqual(slot_entry_2.order, 2)
        self.assertEqual(slot_entry_3.order, 7)
        self.assertEqual(slot_entry_4.order, 8)

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

        self.assertEqual(self.slot_entry.calculate_weight(1), 80)
        self.assertEqual(self.slot_entry.calculate_weight(2), 80)
        self.assertEqual(self.slot_entry.calculate_weight(3), 82.5)
        self.assertEqual(self.slot_entry.calculate_weight(4), 82.5)
        self.assertEqual(self.slot_entry.calculate_weight(5), 82.5)
        self.assertEqual(self.slot_entry.calculate_weight(6), 42)
        self.assertEqual(self.slot_entry.calculate_weight(7), 40)
        self.assertEqual(self.slot_entry.calculate_weight(8), 44)

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
        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
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
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            requirements={'rules': ['weight', 'repetitions']},
        ).save()

        # Replace weight with 42 at iteration 5, no logs needed
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=5,
            value=42,
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
            repetitions=4,
        ).save()

        # Did 5x82.5 at iteration 3
        WorkoutLog(
            exercise_id=1,
            user_id=1,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=3,
            weight=82.5,
            repetitions=5,
        ).save()

        self.assertDictEqual(
            asdict(self.slot_entry.get_config_data(1)),
            asdict(
                SetConfigData(
                    slot_entry_id=self.slot_entry.pk,
                    exercise=1,
                    sets=4,
                    weight=Decimal(80),
                    weight_rounding=Decimal(2.5),
                    weight_unit=1,
                    weight_unit_name='kg',
                    repetitions=Decimal(4),
                    repetitions_unit=1,
                    repetitions_unit_name='Repetitions',
                    repetitions_rounding=2,
                    rir=Decimal(2),
                    rest=120,
                )
            ),
        )

        self.assertDictEqual(
            asdict(self.slot_entry.get_config_data(2)),
            asdict(
                SetConfigData(
                    slot_entry_id=self.slot_entry.pk,
                    exercise=1,
                    sets=4,
                    weight=Decimal(80),
                    weight_rounding=Decimal(2.5),
                    weight_unit=1,
                    weight_unit_name='kg',
                    repetitions=Decimal(4),
                    repetitions_unit=1,
                    repetitions_unit_name='Repetitions',
                    repetitions_rounding=2,
                    rir=Decimal(2),
                    rest=120,
                )
            ),
        )

        self.assertDictEqual(
            asdict(self.slot_entry.get_config_data(3)),
            asdict(
                SetConfigData(
                    slot_entry_id=self.slot_entry.pk,
                    exercise=1,
                    sets=4,
                    weight=Decimal(80),
                    weight_rounding=Decimal('2.5'),
                    weight_unit=1,
                    weight_unit_name='kg',
                    repetitions=Decimal(4),
                    repetitions_unit=1,
                    repetitions_unit_name='Repetitions',
                    repetitions_rounding=2,
                    rir=Decimal(2),
                    rest=120,
                )
            ),
        )

        self.assertDictEqual(
            asdict(self.slot_entry.get_config_data(4)),
            asdict(
                SetConfigData(
                    slot_entry_id=self.slot_entry.pk,
                    exercise=1,
                    sets=4,
                    weight=Decimal(82.5),
                    weight_rounding=Decimal('2.5'),
                    weight_unit=1,
                    weight_unit_name='kg',
                    repetitions=Decimal(4),
                    repetitions_rounding=2,
                    repetitions_unit=1,
                    repetitions_unit_name='Repetitions',
                    rir=Decimal(2),
                    rest=120,
                )
            ),
        )

        self.assertDictEqual(
            asdict(self.slot_entry.get_config_data(5)),
            asdict(
                SetConfigData(
                    slot_entry_id=self.slot_entry.pk,
                    exercise=1,
                    sets=4,
                    weight=Decimal('42.5'),
                    weight_rounding=Decimal('2.5'),
                    weight_unit=1,
                    weight_unit_name='kg',
                    repetitions=Decimal(4),
                    repetitions_rounding=2,
                    repetitions_unit=1,
                    repetitions_unit_name='Repetitions',
                    rir=Decimal(2),
                    rest=120,
                )
            ),
        )

        self.assertDictEqual(
            asdict(self.slot_entry.get_config_data(6)),
            asdict(
                SetConfigData(
                    slot_entry_id=self.slot_entry.pk,
                    exercise=1,
                    sets=4,
                    weight=Decimal(42.5),
                    weight_rounding=Decimal('2.5'),
                    weight_unit=1,
                    weight_unit_name='kg',
                    repetitions=Decimal(4),
                    repetitions_rounding=2,
                    repetitions_unit=1,
                    repetitions_unit_name='Repetitions',
                    rir=Decimal(2),
                    rest=120,
                )
            ),
        )

    def test_requirements_sets_met(self):
        """
        Test that the sets are correctly calculated if there are requirements
        """
        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.repetition_rounding = 2
        self.slot_entry.save()

        # Initial value
        SetsConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=5,
        ).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=50,
        ).save()
        RestConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=90,
        ).save()

        # Increase sets by 1 at iteration 2
        SetsConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=1,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            requirements={'rules': ['weight', 'rest']},
        ).save()

        # Rest is ok
        WorkoutLog(
            exercise_id=1,
            user_id=1,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=1,
            weight=50,
            rest=100,
            repetitions=4,
        ).save()

        self.assertDictEqual(
            asdict(self.slot_entry.get_config_data(1)),
            asdict(
                SetConfigData(
                    slot_entry_id=self.slot_entry.pk,
                    exercise=1,
                    sets=5,
                    weight=Decimal(50),
                    weight_rounding=Decimal(2.5),
                    weight_unit=1,
                    weight_unit_name='kg',
                    rest=Decimal(90),
                )
            ),
        )

        # Sets did increase
        self.assertDictEqual(
            asdict(self.slot_entry.get_config_data(2)),
            asdict(
                SetConfigData(
                    slot_entry_id=self.slot_entry.pk,
                    exercise=1,
                    sets=6,
                    weight=Decimal(50),
                    weight_rounding=Decimal(2.5),
                    weight_unit=1,
                    weight_unit_name='kg',
                    rest=Decimal(90),
                )
            ),
        )

    def test_requirements_sets_unmet(self):
        """
        Test that the sets are correctly calculated if there are requirements
        """

        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.repetition_rounding = 2
        self.slot_entry.save()

        # Initial value
        SetsConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=5,
        ).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=50,
        ).save()
        RestConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=90,
        ).save()

        # Increase sets by 1 at iteration 2
        SetsConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=1,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            requirements={'rules': ['weight', 'rest']},
        ).save()

        # Rest too low
        WorkoutLog(
            exercise_id=1,
            user_id=1,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=1,
            weight=50,
            rest=80,
            repetitions=4,
        ).save()

        self.assertEqual(
            self.slot_entry.get_config_data(1),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=5,
                weight=Decimal(50),
                weight_rounding=Decimal(2.5),
                weight_unit=1,
                weight_unit_name='kg',
                rest=90,
            ),
        )

        # Sets don't increase
        self.assertEqual(
            self.slot_entry.get_config_data(2),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=5,
                weight=Decimal(50),
                weight_rounding=Decimal(2.5),
                weight_unit=1,
                weight_unit_name='kg',
                rest=90,
            ),
        )

    def test_requirements_sets_null_values(self):
        """
        Test that the sets are correctly calculated if there are requirements but
        some values are null (e.g. there is a rule to check for RiR but there is no
        RiR config)
        """

        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.repetition_rounding = 2
        self.slot_entry.save()

        # Initial values
        SetsConfig(slot_entry=self.slot_entry, iteration=1, value=4).save()
        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=80,
        ).save()

        # Increase weight by 2.5 at iteration 2, depends on RiR
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=2.5,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            requirements={'rules': ['rir']},
        ).save()

        # Logs
        WorkoutLog(
            exercise_id=1,
            user_id=1,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=1,
            weight=None,
            rest=80,
            repetitions=4,
            rir=2,
        ).save()

        config_data = self.slot_entry.get_config_data(2)
        self.assertEqual(config_data.rir, None)
        self.assertEqual(config_data.weight, 80)

    def test_weight_config_with_logs_and_range(self):
        """
        Test that the weight is correctly calculated for each step / iteration
        if there are logs and there is a weight / rep range
        """

        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.repetition_rounding = 2
        self.slot_entry.save()

        # Initial value: 5-6 reps x 80-100 kg
        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        MaxRepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=6).save()
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
            repetitions=4,
        ).save()

        # 5x80 at iteration 3
        WorkoutLog(
            exercise_id=1,
            user_id=1,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=3,
            weight=80,
            repetitions=5,
        ).save()

        self.assertEqual(
            self.slot_entry.get_config_data(1),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=1,
                weight=Decimal(80),
                weight_unit=1,
                weight_unit_name='kg',
                max_weight=Decimal(100),
                weight_rounding=Decimal('2.5'),
                repetitions=Decimal(4),
                repetitions_rounding=2,
                repetitions_unit=1,
                repetitions_unit_name='Repetitions',
                max_repetitions=Decimal(6),
                rir=None,
                rest=None,
            ),
        )

        self.assertEqual(
            self.slot_entry.get_config_data(2),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=1,
                weight=Decimal(80),
                weight_unit=1,
                weight_unit_name='kg',
                max_weight=Decimal(100),
                weight_rounding=Decimal('2.5'),
                repetitions=Decimal(4),
                repetitions_unit=1,
                repetitions_unit_name='Repetitions',
                repetitions_rounding=2,
                max_repetitions=Decimal(6),
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
        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        RestConfig(slot_entry=self.slot_entry, iteration=1, value=120).save()
        RiRConfig(slot_entry=self.slot_entry, iteration=1, value=2).save()

        self.assertEqual(
            self.slot_entry.get_config_data(1),
            SetConfigData(exercise=1, sets=2, weight=24, repetitions=1, rir=2, rest=120),
        )
        self.assertEqual(
            self.slot_entry.get_config_data(2),
            SetConfigData(exercise=2, sets=4, weight=42, repetitions=10, rir=1, rest=90),
        )
        self.assertEqual(
            self.slot_entry.get_config_data(3),
            SetConfigData(exercise=2, sets=4, weight=42, repetitions=10, rir=1, rest=90),
        )

    def test_empty_configs(self):
        """
        Test that the correct config is calculated if there are no configs at all
        """
        self.assertDictEqual(
            asdict(self.slot_entry.get_config_data(1)),
            asdict(
                SetConfigData(
                    slot_entry_id=self.slot_entry.pk,
                    exercise=1,
                    sets=1,
                    max_sets=None,
                    weight=None,
                    weight_rounding=None,
                    weight_unit=None,
                    repetitions=None,
                    repetitions_rounding=None,
                    repetitions_unit=None,
                    rir=None,
                    rest=None,
                )
            ),
        )

    def test_has_progression_flag(self):
        """Tests that the has_progression flag is automatically set"""

        self.assertFalse(self.slot_entry.has_progression)
        SetsConfig(slot_entry=self.slot_entry, iteration=1, value=4).save()
        SetsConfig(slot_entry=self.slot_entry, iteration=2, value=6).save()

        self.assertTrue(self.slot_entry.has_progression)

    def test_cache_get_config_data(self):
        """Tests that cache used in get_config_data is correctly (re)set"""

        key = CacheKeyMapper.slot_entry_configs_key(self.slot_entry.pk)

        set_config = SetsConfig(slot_entry=self.slot_entry, iteration=1, value=4)
        set_config.save()

        self.assertIsNone(cache.get(key))
        self.slot_entry.get_config_data(1)
        self.assertTrue(cache.get(key))

        set_config.value = 5
        set_config.save()
        self.assertIsNone(cache.get(key))


class SlotEntryDuplicateConfigTestCase(SimpleTestCase):
    def test_duplicate_configs(self):
        configs = [
            WeightConfig(
                pk=1,
                iteration=1,
                value=80,
                operation=OperationChoices.REPLACE,
                repeat=False,
            ),
            WeightConfig(
                pk=2,
                iteration=2,
                value=2,
                operation=OperationChoices.PLUS,
                repeat=True,
            ),
            WeightConfig(
                pk=3,
                iteration=6,
                value=50,
                operation=OperationChoices.REPLACE,
                repeat=False,
            ),
        ]

        result = SlotEntry.duplicate_configs(
            10,
            configs=configs,
        )

        # Repeats the config of iteration 2 up to the 8th one, the rest remains unchanged
        self.assertEqual(len(result), 6)

        self.assertEqual(result[0].iteration, 1)
        self.assertEqual(result[0].value, 80)

        self.assertEqual(result[1].iteration, 2)
        self.assertEqual(result[1].value, 2)

        self.assertEqual(result[2].iteration, 3)
        self.assertEqual(result[2].value, 2)

        self.assertEqual(result[3].iteration, 4)
        self.assertEqual(result[3].value, 2)

        self.assertEqual(result[4].iteration, 5)
        self.assertEqual(result[4].value, 2)

        self.assertEqual(result[5].iteration, 6)
        self.assertEqual(result[5].value, 50)

    def test_duplicate_configs_2(self):
        """Test that repeat configs can follow each other"""

        configs = [
            WeightConfig(
                pk=1,
                iteration=1,
                value=80,
                operation=OperationChoices.REPLACE,
                repeat=False,
            ),
            WeightConfig(
                pk=2,
                iteration=2,
                value=2,
                operation=OperationChoices.PLUS,
                repeat=True,
            ),
            WeightConfig(
                pk=3,
                iteration=5,
                value=3,
                operation=OperationChoices.MINUS,
                repeat=True,
            ),
        ]

        result = SlotEntry.duplicate_configs(
            10,
            configs=configs,
        )

        # Repeats the config of iteration 2 up to the 8th one, the rest remains unchanged
        self.assertEqual(len(result), 10)

        self.assertEqual(result[0].iteration, 1)
        self.assertEqual(result[0].value, 80)
        self.assertFalse(result[0].repeat)

        self.assertEqual(result[1].iteration, 2)
        self.assertEqual(result[1].value, 2)
        self.assertTrue(result[1].repeat)

        self.assertEqual(result[2].iteration, 3)
        self.assertEqual(result[2].value, 2)
        self.assertTrue(result[2].repeat)

        self.assertEqual(result[3].iteration, 4)
        self.assertEqual(result[3].value, 2)
        self.assertTrue(result[3].repeat)

        self.assertEqual(result[4].iteration, 5)
        self.assertEqual(result[4].value, 3)
        self.assertTrue(result[4].repeat)

        self.assertEqual(result[5].iteration, 6)
        self.assertEqual(result[5].value, 3)
        self.assertTrue(result[5].repeat)
