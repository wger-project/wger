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

# Django
from django.test import SimpleTestCase

# wger
from wger.manager.dataclasses import round_value


class RoundValueTestCase(SimpleTestCase):
    """
    Test that the rounding helper works as expected
    """

    def test_round_value(self):
        self.assertEqual(round_value(5.1, 5), 5)

    def test_round_value2(self):
        self.assertEqual(round_value(Decimal('7'), 1.25), Decimal('7.5'))

    def test_round_value3(self):
        self.assertEqual(round_value(Decimal('3.0'), 0.5), Decimal('3'))

    def test_round_value_base_none(self):
        self.assertEqual(round_value(Decimal('1.33')), Decimal('1.33'))

    def test_round_value_base_zero(self):
        self.assertEqual(round_value(Decimal('1.33'), 0), Decimal('1.33'))

    def test_round_no_value(self):
        self.assertEqual(round_value(None), None)
