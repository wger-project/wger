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
# Standard Library

# wger
from wger.core.tests import api_base_test
from wger.measurements.models import Measurement


class MeasurementsApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the measurements endpoint
    """

    pk = 1
    resource = Measurement
    private_resource = True
    data = {
        'category': 2,
        'date': '2021-08-12',
        'value': 99.99,
    }
