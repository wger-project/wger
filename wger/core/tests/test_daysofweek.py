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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from wger.core.models import DaysOfWeek
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WorkoutManagerTestCase


class DaysOfWeekRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(DaysOfWeek.objects.get(pk=1)), 'Monday')


class DaysOfWeekApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the days of week resource
    '''
    pk = 1
    resource = DaysOfWeek
    private_resource = False
