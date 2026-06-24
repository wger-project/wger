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
