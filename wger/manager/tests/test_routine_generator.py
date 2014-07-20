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

from decimal import Decimal

from wger.manager.routines.helpers import round_weight

from wger.manager.tests.testcase import WorkoutManagerTestCase


class RoutineWeightWeightTestCase(WorkoutManagerTestCase):
    '''
    Test the weight helper for the routines
    '''

    def test_weight(self):
        '''
        Test the weight helper for the routines
        '''
        self.assertEqual(round_weight(1.9), Decimal(2.5))
        self.assertEqual(round_weight(2.1), Decimal(2.5))
        self.assertEqual(round_weight(3), Decimal(2.5))
        self.assertEqual(round_weight(4), Decimal(5))

        self.assertEqual(round_weight(4.5, 5), Decimal(5))
        self.assertEqual(round_weight(6, 5), Decimal(5))
        self.assertEqual(round_weight(7, 5), Decimal(5))
        self.assertEqual(round_weight(8, 5), Decimal(10))
