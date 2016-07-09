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

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.utils.constants import FOURPLACES
from wger.utils.units import AbstractWeight


class WeightConversionTestCase(WorkoutManagerTestCase):
    '''
    Test the abstract weight class
    '''

    def test_conversion(self):
        '''
        Test the weight conversion
        '''

        tmp = AbstractWeight(10)
        self.assertEqual(tmp.kg, 10)
        self.assertEqual(tmp.lb, Decimal(22.0462).quantize(FOURPLACES))

        tmp = AbstractWeight(10, 'lb')
        self.assertEqual(tmp.lb, 10)
        self.assertEqual(tmp.kg, Decimal(4.5359).quantize(FOURPLACES))

        tmp = AbstractWeight(0.4536)
        self.assertEqual(tmp.lb, Decimal(1))
        self.assertEqual(tmp.kg, Decimal(0.4536).quantize(FOURPLACES))

        tmp = AbstractWeight(80)
        self.assertEqual(tmp.lb, Decimal(176.3698).quantize(FOURPLACES))
        self.assertEqual(tmp.kg, 80)

        tmp = AbstractWeight(80, 'kg')
        self.assertEqual(tmp.lb, Decimal(176.3698).quantize(FOURPLACES))
        self.assertEqual(tmp.kg, 80)

    def test_conversion_subunits(self):
        '''
        Test the weight conversion with "subunits" (grams, ounces)
        '''

        tmp = AbstractWeight(100.1, 'g')
        self.assertEqual(tmp.kg, Decimal(0.1001).quantize(FOURPLACES))

        tmp = AbstractWeight(100, 'g')
        self.assertEqual(tmp.kg, Decimal(0.1).quantize(FOURPLACES))

        tmp = AbstractWeight(1000, 'g')
        self.assertEqual(tmp.kg, 1)

        tmp = AbstractWeight(1.5, 'oz')
        self.assertEqual(tmp.lb, Decimal(0.0938).quantize(FOURPLACES))

        tmp = AbstractWeight(2, 'oz')
        self.assertEqual(tmp.lb, Decimal(0.125).quantize(FOURPLACES))

        tmp = AbstractWeight(4, 'oz')
        self.assertEqual(tmp.lb, Decimal(0.25).quantize(FOURPLACES))

        tmp = AbstractWeight(8, 'oz')
        self.assertEqual(tmp.lb, Decimal(0.5).quantize(FOURPLACES))

        tmp = AbstractWeight(16, 'oz')
        self.assertEqual(tmp.lb, 1)

    def test_sum(self):
        '''
        Tests adding two abstract weights
        '''
        weight1 = AbstractWeight(80, 'kg')
        weight2 = AbstractWeight(10, 'kg')
        sum = weight1 + weight2
        self.assertEqual(sum.kg, 90)

        weight1 = AbstractWeight(80, 'kg')
        weight2 = AbstractWeight(10, 'lb')
        sum = weight1 + weight2
        self.assertEqual(sum.kg, Decimal(84.5359).quantize(FOURPLACES))

        weight1 = AbstractWeight(80, 'lb')
        weight2 = AbstractWeight(10, 'lb')
        sum = weight1 + weight2
        self.assertEqual(sum.lb, Decimal(90))

    def test_subunits(self):
        '''
        Test weight subunit calculations
        '''

        tmp = AbstractWeight(10)
        self.assertEqual(tmp.g, 10000)

        tmp = AbstractWeight(2, 'lb')
        self.assertEqual(tmp.oz, 32)
