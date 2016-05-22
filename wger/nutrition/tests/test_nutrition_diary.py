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

from django.core.urlresolvers import reverse

from wger.nutrition.models import NutritionPlan, LogItem
from wger.manager.tests.testcase import (
    WorkoutManagerTestCase,
    WorkoutManagerAccessTestCase,
    WorkoutManagerDeleteTestCase
)

logger = logging.getLogger(__name__)


class DiaryOverviewAccessTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing a nutrition overview page
    '''
    url = reverse('nutrition:log:overview', kwargs={'pk': 1})
    user_success = 'test'
    user_fail = ('admin',
                 'member1',
                 'member2',
                 'trainer2',
                 'trainer3',
                 'trainer4',
                 'manager3',
                 'general_manager1',
                 'general_manager2')


class DiaryOverview2AccessTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing a nutrition overview page (read access activated)
    '''
    url = reverse('nutrition:log:overview', kwargs={'pk': 2})
    user_fail = None
    anonymous_fail = False
    user_success = ('admin',
                    'test',
                    'member1',
                    'member2',
                    'trainer2',
                    'trainer3',
                    'trainer4',
                    'manager3',
                    'general_manager1',
                    'general_manager2')


class DiaryDetailAccessTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing a nutrition overview page
    '''
    url = reverse('nutrition:log:detail', kwargs={'pk': 1,
                                                  'year': 2016,
                                                  'month': 5,
                                                  'day': 15})
    user_success = 'test'
    user_fail = ('admin',
                 'member1',
                 'member2',
                 'trainer2',
                 'trainer3',
                 'trainer4',
                 'manager3',
                 'general_manager1',
                 'general_manager2')


class DiaryDetail2AccessTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing a nutrition overview page (read access activated)
    '''
    url = reverse('nutrition:log:detail', kwargs={'pk': 2,
                                                  'year': 2016,
                                                  'month': 5,
                                                  'day': 15})
    user_fail = None
    anonymous_fail = False
    user_success = ('admin',
                    'test',
                    'member1',
                    'member2',
                    'trainer2',
                    'trainer3',
                    'trainer4',
                    'manager3',
                    'general_manager1',
                    'general_manager2')


class NutritionDiaryTestCase(WorkoutManagerTestCase):
    '''
    Tests the different nutrition diary functions
    '''

    def test_calculations(self):
        plan = NutritionPlan.objects.get(pk=1)

        # No entries for date
        self.assertEqual(plan.get_log_summary(datetime.date(2016, 1, 12)),
                         {'energy': 0,
                          'protein': 0,
                          'carbohydrates': 0,
                          'carbohydrates_sugar': 0,
                          'fat': 0,
                          'fat_saturated': 0,
                          'fibres': 0,
                          'sodium': 0})

        # Entries found
        self.assertEqual(plan.get_log_summary(datetime.date(2016, 5, 15)),
                         {'energy': Decimal('653.80'),
                          'protein': Decimal('19.22'),
                          'carbohydrates': Decimal('109.99'),
                          'carbohydrates_sugar': Decimal('107.72'),
                          'fat': Decimal('9.32'),
                          'fat_saturated': Decimal('2.43'),
                          'fibres': Decimal('0.00'),
                          'sodium': Decimal('5.09')})


class DeleteLogEntryTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting an entry from a nutritional diary
    '''

    object_class = LogItem
    url = 'nutrition:log:delete'
    pk = 2
    user_success = 'test'
    user_success = ('admin',
                    'test',
                    'member1',
                    'member2',
                    'trainer2',
                    'trainer3',
                    'trainer4',
                    'manager3',
                    'general_manager1',
                    'general_manager2')
