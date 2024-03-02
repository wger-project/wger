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

# wger
from wger.core.tests import api_base_test
from wger.nutrition.models import MealItem


class MealItemApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the meal overview resource
    """

    pk = 10
    resource = MealItem
    private_resource = True
    data = {
        'meal': 2,
        'amount': 100,
        'ingredient': 1,
    }
