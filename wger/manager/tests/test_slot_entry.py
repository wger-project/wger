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
    MAX_COMPOUND_RIR,
    MAX_COMPOUND_VALUE,
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

        configs = list(self.slot_entry.weightconfig_set.all())

        self.assertEqual(SlotEntry.walk_config_values(configs, 1), 80)
        self.assertEqual(SlotEntry.walk_config_values(configs, 2), 80)
        self.assertEqual(SlotEntry.walk_config_values(configs, 3), 82.5)
        self.assertEqual(SlotEntry.walk_config_values(configs, 4), 82.5)
        self.assertEqual(SlotEntry.walk_config_values(configs, 5), 82.5)
        self.assertEqual(SlotEntry.walk_config_values(configs, 6), 42)
        self.assertEqual(SlotEntry.walk_config_values(configs, 7), 40)
        self.assertEqual(SlotEntry.walk_config_values(configs, 8), 44)

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

        # The iteration 2 log reached the displayed prescription (4 repetitions
        # after rounding, 80 kg), so the weight advances here
        self.assertDictEqual(
            asdict(self.slot_entry.get_config_data(3)),
            asdict(
                SetConfigData(
                    slot_entry_id=self.slot_entry.pk,
                    exercise=1,
                    sets=4,
                    weight=Decimal('82.5'),
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

    def _setup_gated_weight_progression(self, gate_base_config: bool = False):
        """
        Base weight of 20, +2.5 kg per iteration (repeating), gated on reaching
        the prescribed 5 repetitions
        """
        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.save()

        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=20,
            requirements={'rules': ['repetitions']} if gate_base_config else None,
        ).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=2.5,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            repeat=True,
            requirements={'rules': ['repetitions']},
        ).save()

    def _log_repetitions(self, iteration: int, repetitions: int | None, weight: int = 20):
        WorkoutLog(
            exercise_id=1,
            user_id=1,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=iteration,
            weight=weight,
            repetitions=repetitions,
        ).save()

    def test_requirements_no_backfill_after_skipped_iteration(self):
        """
        A gated progression only advances one step per qualifying iteration and
        doesn't back-fill increments for skipped, non-qualifying iterations
        """
        self._setup_gated_weight_progression()

        # Didn't qualify at iteration 1, qualified at iteration 2
        self._log_repetitions(iteration=1, repetitions=3)
        self._log_repetitions(iteration=2, repetitions=5)

        # No increment earned yet at iteration 2
        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal(20))

        # Iteration 3 prescribes exactly one earned increment, not two
        self.assertEqual(self.slot_entry.get_config_data(3).weight, Decimal('22.5'))

    def test_requirements_gap_between_qualifications(self):
        """
        Qualifying at iterations 2 and 4 only earns exactly two increments
        """
        self._setup_gated_weight_progression()

        self._log_repetitions(iteration=1, repetitions=3)
        self._log_repetitions(iteration=2, repetitions=5)
        self._log_repetitions(iteration=3, repetitions=3)
        self._log_repetitions(iteration=4, repetitions=5)

        self.assertEqual(self.slot_entry.get_config_data(5).weight, Decimal(25))

    def test_requirements_continuous_qualification(self):
        """
        Qualifying at every iteration advances the progression at full speed
        """
        self._setup_gated_weight_progression()

        self._log_repetitions(iteration=1, repetitions=5)
        self._log_repetitions(iteration=2, repetitions=5)
        self._log_repetitions(iteration=3, repetitions=5)

        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal('22.5'))
        self.assertEqual(self.slot_entry.get_config_data(3).weight, Decimal(25))
        self.assertEqual(self.slot_entry.get_config_data(4).weight, Decimal('27.5'))

    def test_requirements_iteration_zero_log_does_not_advance(self):
        """
        A log stamped with iteration 0 doesn't advance a gated progression into
        the config of a later iteration
        """
        self._setup_gated_weight_progression(gate_base_config=True)

        self._log_repetitions(iteration=0, repetitions=5)

        # The +2.5 config only takes effect at iteration 2
        self.assertEqual(self.slot_entry.get_config_data(1).weight, Decimal(20))

    def _setup_gated_deload(self):
        """
        Constant 100 kg with a deload to 80 kg at iteration 6, gated on reaching
        the prescribed weight and 5 repetitions
        """
        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.save()

        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        WeightConfig(slot_entry=self.slot_entry, iteration=1, value=100).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=6,
            value=80,
            operation=OperationChoices.REPLACE,
            requirements={'rules': ['weight', 'repetitions']},
        ).save()

    def test_requirements_deload_without_qualification(self):
        """
        A gated replace config is not applied while the requirements are unmet
        """
        self._setup_gated_deload()

        for i in range(1, 10):
            self._log_repetitions(iteration=i, repetitions=3, weight=90)

        self.assertEqual(self.slot_entry.get_config_data(6).weight, Decimal(100))
        self.assertEqual(self.slot_entry.get_config_data(10).weight, Decimal(100))

    def test_requirements_deload_on_time(self):
        """
        A gated replace config is applied at its own iteration when the
        requirements were met in the iteration before
        """
        self._setup_gated_deload()

        self._log_repetitions(iteration=5, repetitions=5, weight=100)

        self.assertEqual(self.slot_entry.get_config_data(5).weight, Decimal(100))
        self.assertEqual(self.slot_entry.get_config_data(6).weight, Decimal(80))
        self.assertEqual(self.slot_entry.get_config_data(9).weight, Decimal(80))

    def test_requirements_deload_late_qualification(self):
        """
        A gated replace config that wasn't met at its own iteration is applied
        at the next iteration whose logs meet the requirements
        """
        self._setup_gated_deload()

        self._log_repetitions(iteration=7, repetitions=5, weight=100)

        self.assertEqual(self.slot_entry.get_config_data(7).weight, Decimal(100))
        self.assertEqual(self.slot_entry.get_config_data(8).weight, Decimal(80))
        self.assertEqual(self.slot_entry.get_config_data(10).weight, Decimal(80))

    def test_requirements_gated_increment_applied_once(self):
        """
        A gated non-repeating increment is applied exactly once even when the
        requirements are met again on later iterations
        """
        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.save()

        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        WeightConfig(slot_entry=self.slot_entry, iteration=1, value=100).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=6,
            value=5,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            requirements={'rules': ['repetitions']},
        ).save()

        self._log_repetitions(iteration=6, repetitions=5)
        self._log_repetitions(iteration=7, repetitions=5)
        self._log_repetitions(iteration=8, repetitions=5)

        self.assertEqual(self.slot_entry.get_config_data(6).weight, Decimal(100))
        self.assertEqual(self.slot_entry.get_config_data(7).weight, Decimal(105))
        self.assertEqual(self.slot_entry.get_config_data(9).weight, Decimal(105))

    def test_requirements_gated_percent_step(self):
        """
        A gated percent progression compounds only on qualifying iterations
        """
        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        WeightConfig(slot_entry=self.slot_entry, iteration=1, value=100).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=10,
            operation=OperationChoices.PLUS,
            step=StepChoices.PERCENT,
            repeat=True,
            requirements={'rules': ['repetitions']},
        ).save()

        self._log_repetitions(iteration=1, repetitions=5)
        self._log_repetitions(iteration=2, repetitions=3)
        self._log_repetitions(iteration=3, repetitions=5)

        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal(110))
        self.assertEqual(self.slot_entry.get_config_data(3).weight, Decimal(110))
        self.assertEqual(self.slot_entry.get_config_data(4).weight, Decimal(121))
        self.assertEqual(self.slot_entry.get_config_data(5).weight, Decimal(121))

    def test_requirements_gated_minus_step(self):
        """
        A gated minus progression only decreases on qualifying iterations
        """
        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.save()

        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        WeightConfig(slot_entry=self.slot_entry, iteration=1, value=100).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=2.5,
            operation=OperationChoices.MINUS,
            step=StepChoices.ABSOLUTE,
            repeat=True,
            requirements={'rules': ['repetitions']},
        ).save()

        self._log_repetitions(iteration=1, repetitions=5)
        self._log_repetitions(iteration=2, repetitions=3)

        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal('97.5'))
        self.assertEqual(self.slot_entry.get_config_data(3).weight, Decimal('97.5'))
        self.assertEqual(self.slot_entry.get_config_data(4).weight, Decimal('97.5'))

    def test_requirements_multiple_logs_one_step(self):
        """
        Several qualifying logs in the same iteration advance the progression
        by a single step
        """
        self._setup_gated_weight_progression()

        self._log_repetitions(iteration=1, repetitions=5)
        self._log_repetitions(iteration=1, repetitions=6)
        self._log_repetitions(iteration=1, repetitions=3)

        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal('22.5'))
        self.assertEqual(self.slot_entry.get_config_data(3).weight, Decimal('22.5'))

    def test_requirements_not_met_across_logs(self):
        """
        Requirements are only met when a single log fulfils all required fields
        """
        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.save()

        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        WeightConfig(slot_entry=self.slot_entry, iteration=1, value=100).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=2.5,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            repeat=True,
            requirements={'rules': ['weight', 'repetitions']},
        ).save()

        # One log only reaches the weight, the other only the repetitions
        self._log_repetitions(iteration=1, repetitions=3, weight=100)
        self._log_repetitions(iteration=1, repetitions=5, weight=90)

        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal(100))

    def test_requirements_empty_rules(self):
        """
        Configs with an empty rules list progress without qualification
        """
        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=20,
            requirements={'rules': []},
        ).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=2.5,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            repeat=True,
            requirements={'rules': []},
        ).save()

        self.assertEqual(self.slot_entry.get_config_data(1).weight, Decimal(20))
        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal('22.5'))
        self.assertEqual(self.slot_entry.get_config_data(3).weight, Decimal(25))

    def test_requirements_threshold_follows_prescription(self):
        """
        The requirement threshold is the value prescribed for the iteration the
        log belongs to, not the initial value
        """
        self._setup_gated_weight_progression()

        # The prescribed repetitions themselves progress: 5, 6, 7, ...
        RepetitionsConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=1,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            repeat=True,
        ).save()

        self._log_repetitions(iteration=1, repetitions=5)
        self._log_repetitions(iteration=2, repetitions=6)
        self._log_repetitions(iteration=3, repetitions=6)

        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal('22.5'))
        self.assertEqual(self.slot_entry.get_config_data(3).weight, Decimal(25))

        # 6 repetitions no longer meet the prescribed 7
        self.assertEqual(self.slot_entry.get_config_data(4).weight, Decimal(25))

    def test_requirements_null_log_value(self):
        """
        A log without a value for a required field does not qualify
        """
        self._setup_gated_weight_progression()

        self._log_repetitions(iteration=1, repetitions=None)

        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal(20))

    def test_requirements_other_user_logs_ignored(self):
        """
        Qualifying logs of other users do not advance the progression
        """
        self._setup_gated_weight_progression()

        WorkoutLog(
            exercise_id=1,
            user_id=2,
            routine_id=1,
            slot_entry=self.slot_entry,
            iteration=1,
            weight=20,
            repetitions=5,
        ).save()

        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal(20))

    def test_config_data_iteration_below_one(self):
        """
        Iterations below one return the iteration 1 configuration
        """
        WeightConfig(slot_entry=self.slot_entry, iteration=1, value=20).save()

        self.assertEqual(self.slot_entry.get_config_data(0).weight, Decimal(20))

    def test_max_weight_not_above_weight_not_emitted(self):
        """
        A max weight that is not above the weight is not part of the config data
        """
        WeightConfig(slot_entry=self.slot_entry, iteration=1, value=100).save()
        MaxWeightConfig(slot_entry=self.slot_entry, iteration=1, value=100).save()

        config_data = self.slot_entry.get_config_data(1)
        self.assertEqual(config_data.weight, Decimal(100))
        self.assertEqual(config_data.max_weight, None)

    def test_requirements_multi_phase_progression(self):
        """
        A later gated config takes over at its scheduled iteration and applies
        its own increment to the earned value
        """
        self._setup_gated_weight_progression()

        # Bigger jumps from iteration 6 on
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=6,
            value=5,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            repeat=True,
            requirements={'rules': ['repetitions']},
        ).save()

        # Qualifies at every second iteration
        for i in range(1, 9):
            self._log_repetitions(iteration=i, repetitions=5 if i % 2 == 0 else 3)

        self.assertEqual(self.slot_entry.get_config_data(3).weight, Decimal('22.5'))
        self.assertEqual(self.slot_entry.get_config_data(5).weight, Decimal(25))

        # From iteration 6 on each earned step is +5
        self.assertEqual(self.slot_entry.get_config_data(7).weight, Decimal(30))
        self.assertEqual(self.slot_entry.get_config_data(9).weight, Decimal(35))
        self.assertEqual(self.slot_entry.get_config_data(10).weight, Decimal(35))

    def test_ungated_config_ignores_unearned_gated_steps(self):
        """
        An ungated config applies on schedule without back-applying the
        increments of earlier non-qualifying gated configs
        """
        self.slot_entry.weight_rounding = 2.5
        self.slot_entry.save()

        RepetitionsConfig(slot_entry=self.slot_entry, iteration=1, value=5).save()
        WeightConfig(slot_entry=self.slot_entry, iteration=1, value=80).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=2.5,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            repeat=True,
            requirements={'rules': ['repetitions']},
        ).save()
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=5,
            value=10,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
        ).save()

        # No qualifying logs at all
        self.assertEqual(self.slot_entry.get_config_data(4).weight, Decimal(80))
        self.assertEqual(self.slot_entry.get_config_data(5).weight, Decimal(90))
        self.assertEqual(self.slot_entry.get_config_data(6).weight, Decimal(90))

    def test_requirements_threshold_uses_rounded_value(self):
        """
        The requirement threshold is the rounded value as it is displayed
        """
        self._setup_gated_weight_progression()

        # The prescribed 5 repetitions are displayed as 4
        self.slot_entry.repetition_rounding = 2
        self.slot_entry.save()

        self._log_repetitions(iteration=1, repetitions=4)

        self.assertEqual(self.slot_entry.get_config_data(2).weight, Decimal('22.5'))

    def test_max_config_follows_base_requirements(self):
        """
        Max configs advance together with the gated base config
        """
        self._setup_gated_weight_progression()

        MaxWeightConfig(slot_entry=self.slot_entry, iteration=1, value=25).save()
        MaxWeightConfig(
            slot_entry=self.slot_entry,
            iteration=2,
            value=2.5,
            operation=OperationChoices.PLUS,
            step=StepChoices.ABSOLUTE,
            repeat=True,
        ).save()

        self._log_repetitions(iteration=1, repetitions=3)
        self._log_repetitions(iteration=2, repetitions=5)

        config_data = self.slot_entry.get_config_data(3)
        self.assertEqual(config_data.weight, Decimal('22.5'))
        self.assertEqual(config_data.max_weight, Decimal('27.5'))

        # No further qualification, both bounds hold
        config_data = self.slot_entry.get_config_data(5)
        self.assertEqual(config_data.weight, Decimal('22.5'))
        self.assertEqual(config_data.max_weight, Decimal('27.5'))

    def test_weight_config_with_logs_and_range(self):
        """
        Test that the weight is correctly calculated for each step / iteration
        if there are logs and there is a weight / rep range.

        Also covers that the upper bound of the range progresses across iterations
        and is not pinned to the value of the first iteration.
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

        # Upper bound rises to 8 reps x 120 kg at iteration 3
        MaxWeightConfig(slot_entry=self.slot_entry, iteration=3, value=120).save()
        MaxRepetitionsConfig(slot_entry=self.slot_entry, iteration=3, value=8).save()

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

        # The upper bound has progressed to its iteration-3 value
        self.assertEqual(
            self.slot_entry.get_config_data(3),
            SetConfigData(
                slot_entry_id=self.slot_entry.pk,
                exercise=1,
                sets=1,
                weight=Decimal(80),
                weight_unit=1,
                weight_unit_name='kg',
                max_weight=Decimal(120),
                weight_rounding=Decimal('2.5'),
                repetitions=Decimal(4),
                repetitions_unit=1,
                repetitions_unit_name='Repetitions',
                repetitions_rounding=2,
                max_repetitions=Decimal(8),
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

    def test_delayed_config_not_served_from_constant_cache(self):
        """
        A config that only takes effect after the first iteration yields a different
        result per iteration, so priming the cache with iteration 1 must not poison
        the result of a later iteration
        """
        WeightConfig(slot_entry=self.slot_entry, iteration=3, value=100).save()

        # Iteration 1, where the config is not active yet, populates the cache
        self.assertIsNone(self.slot_entry.get_config_data(1).weight)

        # Iteration 3 must reflect the config, not the cached iteration-1 result
        self.assertEqual(self.slot_entry.get_config_data(3).weight, Decimal(100))


class WalkConfigValuesTestCase(SimpleTestCase):
    """
    Tests for the ungated config walk
    """

    @staticmethod
    def _walk_series(configs, iterations: int):
        return [SlotEntry.walk_config_values(configs, i) for i in range(1, iterations + 1)]

    def test_repeat_expansion(self):
        """A repeating config applies every iteration until another config takes over"""

        configs = [
            WeightConfig(
                iteration=1,
                value=80,
                operation=OperationChoices.REPLACE,
                repeat=False,
            ),
            WeightConfig(
                iteration=2,
                value=2,
                operation=OperationChoices.PLUS,
                repeat=True,
            ),
            WeightConfig(
                iteration=6,
                value=50,
                operation=OperationChoices.REPLACE,
                repeat=False,
            ),
        ]

        self.assertEqual(
            self._walk_series(configs, 10),
            [80, 82, 84, 86, 88, 50, 50, 50, 50, 50],
        )

    def test_chained_repeats(self):
        """Repeat configs can follow each other"""

        configs = [
            WeightConfig(
                iteration=1,
                value=80,
                operation=OperationChoices.REPLACE,
                repeat=False,
            ),
            WeightConfig(
                iteration=2,
                value=2,
                operation=OperationChoices.PLUS,
                repeat=True,
            ),
            WeightConfig(
                iteration=5,
                value=3,
                operation=OperationChoices.MINUS,
                repeat=True,
            ),
        ]

        self.assertEqual(
            self._walk_series(configs, 10),
            [80, 82, 84, 86, 83, 80, 77, 74, 71, 68],
        )

    def test_hold_without_repeat(self):
        """A non-repeating config applies once and the value holds afterwards"""

        configs = [
            WeightConfig(iteration=1, value=80, operation=OperationChoices.REPLACE),
            WeightConfig(iteration=3, value=2.5, operation=OperationChoices.PLUS),
        ]

        self.assertEqual(
            self._walk_series(configs, 5),
            [80, 80, Decimal('82.5'), Decimal('82.5'), Decimal('82.5')],
        )

    def test_no_configs(self):
        self.assertIsNone(SlotEntry.walk_config_values([], 5))

    def test_compound_weight_is_capped(self):
        """Percent progressions can't push the output past MAX_COMPOUND_VALUE"""

        configs = [
            WeightConfig(iteration=1, value=100, operation=OperationChoices.REPLACE),
            # +50% per iteration, repeated enough times to blow past 9999.99
            WeightConfig(
                iteration=2,
                value=50,
                operation=OperationChoices.PLUS,
                step=StepChoices.PERCENT,
                repeat=True,
            ),
        ]

        result = SlotEntry.walk_config_values(configs, 19)

        self.assertEqual(result, MAX_COMPOUND_VALUE)

    def test_rir_is_capped_at_rir_max(self):
        """RiR uses the tighter cap (max_digits=2, decimal_places=1)"""

        configs = [
            RiRConfig(iteration=1, value=2, operation=OperationChoices.REPLACE),
            RiRConfig(iteration=2, value=50, operation=OperationChoices.PLUS),
        ]

        result = SlotEntry.walk_config_values(configs, 2, max_value=MAX_COMPOUND_RIR)

        self.assertEqual(result, MAX_COMPOUND_RIR)

    def test_value_below_cap_is_unchanged(self):
        configs = [
            WeightConfig(iteration=1, value=80, operation=OperationChoices.REPLACE),
            WeightConfig(iteration=2, value=5, operation=OperationChoices.PLUS),
        ]

        result = SlotEntry.walk_config_values(configs, 2)

        self.assertEqual(result, Decimal(85))
