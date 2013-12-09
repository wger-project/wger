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

import datetime

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.utils.helpers import next_weekday


class IcalToolsTestCase(WorkoutManagerTestCase):
    '''
    Tests some tools used for iCal generation
    '''

    def test_next_weekday(self):
        '''
        Test the next weekday function
        '''
        start_date = datetime.date(2013, 12, 5)

        # Find next monday
        self.assertEqual(next_weekday(start_date, 0), datetime.date(2013, 12, 9))

        # Find next wednesday
        self.assertEqual(next_weekday(start_date, 2), datetime.date(2013, 12, 11))

        # Find next saturday
        self.assertEqual(next_weekday(start_date, 5), datetime.date(2013, 12, 7))
