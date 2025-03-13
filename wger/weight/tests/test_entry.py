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
import datetime

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.weight.models import WeightEntry


class MealRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(str(WeightEntry.objects.get(pk=1)), '2012-10-01: 77.00 kg')


class WeightEntryTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the weight entry overview resource
    """

    pk = 3
    resource = WeightEntry
    private_resource = True
    data = {'weight': 100, 'date': datetime.date(2013, 2, 1)}
