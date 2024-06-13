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

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.dataclasses import SetConfigData


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
            reps=4,
            reps_unit=1,
            weight=20,
            weight_unit=1,
            rir=3,
            rest=40,
        )

    def test_text_repr(self):
        self.assertEqual(self.config.text_repr, '4 × 20 kg @ 3 RiR')

    def test_normalize_decimals(self):
        self.config.weight = 22.50
        self.assertEqual(self.config.text_repr, '4 × 22.5 kg @ 3 RiR')

    def test_weight_unit(self):
        self.config.weight_unit = 2
        self.assertEqual(self.config.text_repr, '4 × 20 lb @ 3 RiR')

    def test_no_rir(self):
        self.config.rir = None
        self.assertEqual(self.config.text_repr, '4 × 20 kg')

    def test_no_weight(self):
        self.config.weight = None
        self.assertEqual(self.config.text_repr, '4 × @ 3 RiR')

    def test_sets(self):
        self.config.sets = 3
        self.assertEqual(self.config.text_repr, '3 Sets – 4 × 20 kg @ 3 RiR')

    def test_weight_rounding(self):
        self.config.weight = 22.499
        self.config.weight_rounding = 5
        self.assertEqual(self.config.text_repr, '4 × 20 kg @ 3 RiR')

    def test_reps_unit(self):
        self.config.reps = 90
        self.config.reps_unit = 3
        self.assertEqual(self.config.text_repr, '90 Seconds × 20 kg @ 3 RiR')

    def test_reps_rounding(self):
        self.config.reps = 4.72
        self.config.reps_rounding = 2.5
        self.assertEqual(self.config.text_repr, '5 × 20 kg @ 3 RiR')

    def test_rir_rounding(self):
        self.config.rir = 2.50
        self.assertEqual(self.config.text_repr, '4 × 20 kg @ 2.5 RiR')

    def test_amrap(self):
        self.config.reps_unit = 2
        self.assertEqual(self.config.text_repr, '∞ × 20 kg @ 3 RiR')
