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

import logging
import datetime
from decimal import Decimal

from wger.nutrition.models import NutritionPlan
from wger.manager.tests.testcase import WorkoutManagerTestCase

logger = logging.getLogger(__name__)


class NutritionDiaryTestCase(WorkoutManagerTestCase):
    '''
    Tests the different nutrition diary functions
    '''

    def test_calculations(self):
        plan = NutritionPlan.objects.get(pk=1)

        # No entries for date
        self.assertEqual(plan.get_logged_values(datetime.date(2016, 1, 12)),
                         {'energy': 0,
                          'protein': 0,
                          'carbohydrates': 0,
                          'carbohydrates_sugar': 0,
                          'fat': 0,
                          'fat_saturated': 0,
                          'fibres': 0,
                          'sodium': 0})

        # Entries found
        self.assertEqual(plan.get_logged_values(datetime.date(2016, 5, 15)),
                         {'energy': Decimal('653.80'),
                          'protein': Decimal('19.22'),
                          'carbohydrates': Decimal('109.99'),
                          'carbohydrates_sugar': Decimal('107.72'),
                          'fat': Decimal('9.32'),
                          'fat_saturated': Decimal('2.43'),
                          'fibres': Decimal('0.00'),
                          'sodium': Decimal('5.09')})
