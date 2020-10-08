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
import datetime
import logging
from decimal import Decimal

# Django
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import (
    WgerAccessTestCase,
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerTestCase
)
from wger.nutrition.models import (
    LogItem,
    NutritionPlan
)


logger = logging.getLogger(__name__)


class DiaryOverviewAccessTest(WgerAccessTestCase):
    """
    Tests accessing a nutrition overview page
    """
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


class DiaryOverview2AccessTest(WgerAccessTestCase):
    """
    Tests accessing a nutrition overview page (read access activated)
    """
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


class DiaryDetailAccessTest(WgerAccessTestCase):
    """
    Tests accessing a nutrition overview page
    """
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


class DiaryDetail2AccessTest(WgerAccessTestCase):
    """
    Tests accessing a nutrition overview page (read access activated)
    """
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


class NutritionDiaryTestCase(WgerTestCase):
    """
    Tests the different nutrition diary functions
    """

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

    def test_log_meal(self):
        """
        Tests that logging a meal creates log entries for all meals
        """
        plan = NutritionPlan.objects.get(pk=1)

        LogItem.objects.all().delete()
        self.assertFalse(LogItem.objects.filter(plan=plan))
        self.user_login('test')
        response = self.client.get(reverse('nutrition:log:log_meal', kwargs={"meal_pk": 1}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(LogItem.objects.filter(plan=plan).count(), 3)

    def test_log_meal_logged_out(self):
        """
        Tests that logging a meal doesn't work for a logged out user
        """
        plan = NutritionPlan.objects.get(pk=1)
        LogItem.objects.all().delete()
        self.assertFalse(LogItem.objects.filter(plan=plan))
        response = self.client.get(reverse('nutrition:log:log_meal', kwargs={"meal_pk": 1}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(LogItem.objects.filter(plan=plan).count(), 0)

    def test_log_meal_other_user(self):
        """
        Tests that logging a meal doesn't work for a logged out user
        """
        plan = NutritionPlan.objects.get(pk=1)
        LogItem.objects.all().delete()
        self.assertFalse(LogItem.objects.filter(plan=plan))
        self.user_login('admin')
        response = self.client.get(reverse('nutrition:log:log_meal', kwargs={"meal_pk": 1}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(LogItem.objects.filter(plan=plan).count(), 0)

    def test_log_plan(self):
        """
        Tests that logging a plan creates a log entry for all meals within the plan
        """
        plan = NutritionPlan.objects.get(pk=1)
        LogItem.objects.all().delete()
        self.assertFalse(LogItem.objects.filter(plan=plan))
        self.user_login('test')
        response = self.client.get(
            reverse('nutrition:log:log_plan', kwargs={"plan_pk": 1}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(LogItem.objects.filter(plan=plan).count(), 3)

    def test_log_plan_logged_out(self):
        """
        Tests that logging a plan doesn't work for a logged out user
        """
        plan = NutritionPlan.objects.get(pk=1)
        LogItem.objects.all().delete()
        self.assertFalse(LogItem.objects.filter(plan=plan))
        response = self.client.get(
            reverse('nutrition:log:log_plan', kwargs={"plan_pk": 1}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(LogItem.objects.filter(plan=plan).count(), 0)

    def test_log_plan_other_user(self):
        """
        Tests that logging a plan doesn't work for a logged out user
        """
        plan = NutritionPlan.objects.get(pk=1)
        LogItem.objects.all().delete()
        self.assertFalse(LogItem.objects.filter(plan=plan))
        self.user_login('admin')
        response = self.client.get(
            reverse('nutrition:log:log_plan', kwargs={"plan_pk": 1}))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(LogItem.objects.filter(plan=plan).count(), 0)


class AddMealItemUnitTestCase(WgerAddTestCase):
    """
    Tests adding a meal, set the amount using a unit
    """

    user_success = 'test'
    user_fail = 'admin'
    object_class = LogItem
    url = reverse('nutrition:log:add', kwargs={'plan_pk': 1})
    data = {'amount': 1,
            'ingredient': 1,
            'weight_unit': 1}


class DeleteLogEntryTestCase(WgerDeleteTestCase):
    """
    Tests deleting an entry from a nutritional diary
    """

    object_class = LogItem
    url = 'nutrition:log:delete'
    pk = 2
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
