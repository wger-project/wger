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
from wger.nutrition.models import NutritionPlan


class PlanApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the nutritional plan overview resource

    TODO: setting overview_cached to true since get_nutritional_values is
          cached, but we don't really use it. This should be removed
    """

    pk = 4
    resource = NutritionPlan
    private_resource = True
    overview_cached = False
    special_endpoints = ('nutritional_values',)
    data = {'description': 'The description'}
