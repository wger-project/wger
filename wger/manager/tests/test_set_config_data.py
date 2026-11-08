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
from wger.manager.api.serializers import SetConfigDataSerializer
from wger.manager.dataclasses import (
    SetConfigData,
    SlotData,
    round_value,
)
from wger.manager.models.abstract_config import MAX_COMPOUND_RIR


class SetConfigDataTestCase(WgerTestCase):
    """
    Test that the text representation works as expected
    """

    config: SetConfigData

    def setUp(self):
        super().setUp()

        self.config = SetConfigData(
            exercise=1,
            type='normal',
            sets=1,
            repetitions=4,
            repetitions_unit=1,
            weight=20,
            weight_unit=1,
            weight_unit_name='kg',
            rir=3,
            rest=None,
        )

    def test_text_repr(self):
        self.assertEqual(self.config.text_repr, '4 × 20 kg @ 3 RiR')

    def test_text_repr_normalize_decimals(self):
        self.config.weight = 22.50
        self.assertEqual(self.config.text_repr, '4 × 22.5 kg @ 3 RiR')

    def test_text_repr_weight_unit(self):
        self.config.weight_unit = 2
        self.config.weight_unit_name = 'lb'
        self.assertEqual(self.config.text_repr, '4 × 20 lb @ 3 RiR')

    def test_text_repr_no_rir(self):
        self.config.rir = None
        self.assertEqual(self.config.text_repr, '4 × 20 kg')

    def test_text_repr_no_weight(self):
        self.config.weight = None
        self.assertEqual(self.config.text_repr, '4 Reps @ 3 RiR')

    def test_text_repr_sets(self):
        self.config.sets = 3
        self.assertEqual(self.config.text_repr, '3 Sets, 4 × 20 kg @ 3 RiR')

    def test_text_repr_max_sets(self):
        self.config.sets = 3
        self.config.max_sets = 6
        self.assertEqual(self.config.text_repr, '3-6 Sets, 4 × 20 kg @ 3 RiR')

    def test_text_repr_weight_rounding(self):
        self.config.weight = 22.499
        self.config.weight_rounding = 5
        self.assertEqual(self.config.text_repr, '4 × 20 kg @ 3 RiR')

    def test_text_repr_reps_unit(self):
        self.config.repetitions = 90
        self.config.repetitions_unit = 3
        self.config.repetitions_unit_name = 'Seconds'
        self.assertEqual(self.config.text_repr, '90 Seconds × 20 kg @ 3 RiR')

    def test_text_repr_reps_unit_no_weight(self):
        self.config.repetitions = 90
        self.config.repetitions_unit = 3
        self.config.repetitions_unit_name = 'Seconds'
        self.config.weight = None
        self.assertEqual(self.config.text_repr, '90 Seconds @ 3 RiR')

    def test_text_repr_reps_rounding(self):
        self.config.repetitions = 4.72
        self.config.repetitions_rounding = 2.5
        self.assertEqual(self.config.text_repr, '5 × 20 kg @ 3 RiR')

    def test_text_repr_rir_rounding(self):
        self.config.rir = 2.50
        self.assertEqual(self.config.text_repr, '4 × 20 kg @ 2.5 RiR')

    def test_text_repr_amrap(self):
        self.config.repetitions_unit = 2
        self.assertEqual(self.config.text_repr, '∞ × 20 kg @ 3 RiR')

    def test_text_repr_reps_range(self):
        self.config.max_repetitions = 6
        self.assertEqual(self.config.text_repr, '4-6 × 20 kg @ 3 RiR')

    def test_text_repr_weight_range(self):
        self.config.max_weight = 30
        self.assertEqual(self.config.text_repr, '4 × 20-30 kg @ 3 RiR')

    def test_text_repr_sets_and_weight_range(self):
        self.config.sets = 3
        self.config.max_weight = 30
        self.assertEqual(self.config.text_repr, '3 Sets, 4 × 20-30 kg @ 3 RiR')

    def test_text_repr_sets_weight_and_rest_range(self):
        self.config.sets = 3
        self.config.max_weight = 30
        self.config.rest = 100
        self.config.max_rest = 120
        self.assertEqual(self.config.text_repr, '3 Sets, 4 × 20-30 kg @ 3 RiR 100-120s rest')

    def test_text_repr_sets_weight_and_rest(self):
        self.config.sets = 3
        self.config.rest = 100
        self.assertEqual(self.config.text_repr, '3 Sets, 4 × 20 kg @ 3 RiR 100s rest')

    def test_text_repr_only_sets(self):
        self.config.sets = 3
        self.config.weight = None
        self.config.max_weight = None
        self.config.max_repetitions = None
        self.config.repetitions = None
        self.config.rir = None
        self.assertEqual(self.config.text_repr, '3 Sets')

    def test_rpe_calculation_1(self):
        self.assertEqual(self.config.rpe, 7)

    def test_rpe_calculation_2(self):
        self.config.rir = 1
        self.assertEqual(self.config.rpe, 9)

    def test_no_rpe_calculation(self):
        self.config.rir = None
        self.assertEqual(self.config.rpe, None)

    def test_high_rpe_calculation(self):
        self.config.rir = 7
        self.assertEqual(self.config.rpe, 4)

    def test_rpe_max_effort(self):
        """RiR 0 (no reps in reserve = maximum effort) maps to RPE 10, not None."""
        self.config.rir = 0
        self.assertEqual(self.config.rpe, 10)

    def test_rpe_10_serializes_without_overflow(self):
        """
        RPE 10 (derived from RiR 0) must fit the serializer's DecimalField; a
        two-digit field would raise decimal.InvalidOperation on the routine
        date-sequence endpoints.
        """
        self.config.rir = 0

        data = SetConfigDataSerializer(self.config).data

        self.assertEqual(Decimal(data['rpe']), Decimal('10'))

    def test_capped_rir_serializes_without_overflow(self):
        """
        get_config rounds RiR to the nearest 0.5 before serialization, so the
        compound safety cap must round to a value that still fits the two-digit
        DecimalField. A cap that rounds up to 10.0 raises
        decimal.InvalidOperation and 500s the routine date-sequence endpoints.
        """
        capped_rir = round_value(MAX_COMPOUND_RIR, 0.5)
        self.config.rir = capped_rir

        data = SetConfigDataSerializer(self.config).data

        self.assertEqual(Decimal(data['rir']), capped_rir)


class SetConfigDataUnitsTestCase(WgerTestCase):
    """
    Test the long and short text representation for the different units
    """

    def assert_texts(self, config: SetConfigData, text_repr: str, text_repr_short: str):
        self.assertEqual(config.text_repr, text_repr)
        self.assertEqual(config.text_repr_short, text_repr_short)

    def test_seconds(self):
        config = SetConfigData(
            exercise=1,
            repetitions=45,
            repetitions_unit=3,
            repetitions_unit_name='Seconds',
            rest=15,
        )
        self.assert_texts(config, '45 Seconds 15s rest', '45 Seconds')

    def test_until_failure_with_weight_without_repetitions(self):
        config = SetConfigData(
            exercise=1,
            repetitions_unit=2,
            repetitions_unit_name='Until Failure',
            weight=20,
            weight_unit=1,
            weight_unit_name='kg',
            rir=2,
            rest=15,
        )
        self.assert_texts(config, '∞ × 20 kg @ 2 RiR 15s rest', '∞ × 20 kg')

    def test_until_failure_without_repetitions(self):
        config = SetConfigData(
            exercise=1,
            repetitions_unit=2,
            repetitions_unit_name='Until Failure',
            rest=15,
        )
        self.assert_texts(config, 'Until Failure 15s rest', 'Until Failure')

    def test_max_reps_without_repetitions(self):
        config = SetConfigData(
            exercise=1,
            repetitions_unit=7,
            repetitions_unit_name='Max Reps',
            rest=15,
        )
        self.assert_texts(config, 'Max Reps 15s rest', 'Max Reps')

    def test_max_reps_with_weight_without_repetitions(self):
        config = SetConfigData(
            exercise=1,
            repetitions_unit=7,
            repetitions_unit_name='Max Reps',
            weight=20,
            weight_unit=1,
            weight_unit_name='kg',
        )
        self.assert_texts(config, 'Max Reps × 20 kg', 'Max Reps × 20 kg')

    def test_kilometers_and_speed(self):
        config = SetConfigData(
            exercise=1,
            repetitions=5,
            repetitions_unit=6,
            repetitions_unit_name='Kilometers',
            weight=12,
            weight_unit=6,
            weight_unit_name='Kilometers Per Hour',
            rest=15,
        )
        self.assert_texts(
            config,
            '5 Kilometers × 12 Kilometers Per Hour 15s rest',
            '5 Kilometers × 12 Kilometers Per Hour',
        )

    def test_pounds(self):
        config = SetConfigData(
            exercise=1,
            repetitions=8,
            repetitions_unit=1,
            repetitions_unit_name='Repetitions',
            weight=65,
            weight_unit=2,
            weight_unit_name='lb',
            rest=15,
        )
        self.assert_texts(config, '8 × 65 lb 15s rest', '8 × 65 lb')

    def test_body_weight_zero(self):
        config = SetConfigData(
            exercise=1,
            repetitions=10,
            repetitions_unit=1,
            repetitions_unit_name='Repetitions',
            weight=0,
            weight_unit=5,
            weight_unit_name='Body Weight',
            rest=15,
        )
        self.assert_texts(config, '10 Reps 15s rest', '10 Reps')

    def test_plates(self):
        config = SetConfigData(
            exercise=1,
            repetitions=8,
            repetitions_unit=1,
            repetitions_unit_name='Repetitions',
            weight=2,
            weight_unit=3,
            weight_unit_name='Plates',
            rest=15,
        )
        self.assert_texts(config, '8 × 2 Plates 15s rest', '8 × 2 Plates')

    def test_ranges(self):
        config = SetConfigData(
            exercise=1,
            sets=3,
            repetitions=8,
            max_repetitions=12,
            repetitions_unit=1,
            repetitions_unit_name='Repetitions',
            weight=60,
            max_weight=70,
            weight_unit=1,
            weight_unit_name='kg',
            rir=2,
            rest=15,
            max_rest=30,
        )
        self.assert_texts(
            config,
            '3 Sets, 8-12 × 60-70 kg @ 2 RiR 15-30s rest',
            '8-12 × 60-70 kg',
        )

    def test_weight_only(self):
        config = SetConfigData(
            exercise=1,
            weight=40,
            weight_unit=1,
            weight_unit_name='kg',
            rest=15,
        )
        self.assert_texts(config, '40 kg 15s rest', '40 kg')

    def test_short_text_serialized(self):
        config = SetConfigData(
            exercise=1,
            sets=3,
            repetitions=8,
            repetitions_unit=1,
            weight=40,
            weight_unit=1,
            weight_unit_name='kg',
            rest=15,
        )
        data = SetConfigDataSerializer(config).data

        self.assertEqual(data['text_repr'], '3 Sets, 8 × 40 kg 15s rest')
        self.assertEqual(data['text_repr_short'], '8 × 40 kg')


class SlotDataExercisesTestCase(WgerTestCase):
    """
    Test that the list of exercises of a slot keeps the order of its sets
    """

    def test_exercises_keep_set_order(self):
        # Two rounds of a circuit, the ids are chosen so that a plain set
        # would return them in a different order
        exercise_ids = [2034, 2115, 974, 2108, 2116] * 2
        slot_data = SlotData(
            comment='',
            sets=[SetConfigData(exercise=i, sets=1) for i in exercise_ids],
        )

        self.assertEqual(slot_data.exercises, [2034, 2115, 974, 2108, 2116])
        self.assertTrue(slot_data.is_superset)
