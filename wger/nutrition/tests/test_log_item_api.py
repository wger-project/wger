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

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.nutrition.models import LogItem


PLAN_OWNED = 'cc000000-0000-0000-0000-000000000001'
"""Belongs to user 'test', has four diary entries"""

PLAN_OTHER = 'cc000000-0000-0000-0000-000000000002'
"""Belongs to user 'admin', has one diary entry"""

LOG_OWNED = 'ee000000-0000-0000-0000-000000000001'
LOG_OTHER = '44444444-4444-4444-4444-000000000005'


class LogItemApiTestCase(BaseTestCase, ApiBaseTestCase):
    """
    Tests the nutrition diary endpoint

    The diary of user 'test' has three entries on 2016-05-15 and one on
    2016-05-14.
    """

    url = '/api/v2/nutritiondiary/'

    def get_ids(self, response) -> list:
        return [entry['id'] for entry in response.json()['results']]

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_is_scoped_to_the_owner(self):
        self.authenticate('test')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.get_ids(response)), 4)
        self.assertNotIn(LOG_OTHER, self.get_ids(response))

    def test_detail_other_user(self):
        self.authenticate('test')
        response = self.client.get(f'{self.url}{LOG_OTHER}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_date(self):
        """The date filter uses the local date of the entry's timestamp"""
        self.authenticate('test')

        response = self.client.get(self.url, {'datetime__date': '2016-05-15'})
        self.assertEqual(len(self.get_ids(response)), 3)

        response = self.client.get(self.url, {'datetime__date': '2016-05-14'})
        self.assertEqual(len(self.get_ids(response)), 1)

        response = self.client.get(self.url, {'datetime__date': '2016-05-16'})
        self.assertEqual(self.get_ids(response), [])

    def test_filter_by_datetime_range(self):
        self.authenticate('test')

        response = self.client.get(self.url, {'datetime__gte': '2016-05-15T00:00:00Z'})
        self.assertEqual(len(self.get_ids(response)), 3)

        response = self.client.get(self.url, {'datetime__lt': '2016-05-15T00:00:00Z'})
        self.assertEqual(len(self.get_ids(response)), 1)

    def test_filter_by_plan_cannot_leak(self):
        """Filtering by a foreign plan returns nothing, not that plan's entries"""
        self.authenticate('test')
        response = self.client.get(self.url, {'plan': PLAN_OTHER})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.get_ids(response), [])

    def test_post_to_own_plan(self):
        self.authenticate('test')
        count_before = LogItem.objects.count()

        response = self.client.post(
            self.url,
            data={
                'plan': PLAN_OWNED,
                'ingredient': 1,
                'amount': 100,
                'datetime': '2016-05-16T10:00:00Z',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LogItem.objects.count(), count_before + 1)
        self.assertEqual(str(LogItem.objects.get(pk=response.json()['id']).plan_id), PLAN_OWNED)

    def test_post_to_other_users_plan(self):
        """A diary entry cannot be written into somebody else's plan"""
        self.authenticate('test')
        count_before = LogItem.objects.count()

        response = self.client.post(
            self.url,
            data={
                'plan': PLAN_OTHER,
                'ingredient': 1,
                'amount': 100,
                'datetime': '2016-05-16T10:00:00Z',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(LogItem.objects.count(), count_before)

    def test_patch_other_user_entry(self):
        self.authenticate('test')
        response = self.client.patch(f'{self.url}{LOG_OTHER}/', data={'amount': 1})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(LogItem.objects.get(pk=LOG_OTHER).amount, 75)

    def test_delete_other_user_entry(self):
        self.authenticate('test')
        response = self.client.delete(f'{self.url}{LOG_OTHER}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(LogItem.objects.filter(pk=LOG_OTHER).exists())

    def test_delete_own_entry(self):
        self.authenticate('test')
        response = self.client.delete(f'{self.url}{LOG_OWNED}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LogItem.objects.filter(pk=LOG_OWNED).exists())

    def test_nutritional_values_action(self):
        self.authenticate('test')
        response = self.client.get(f'{self.url}{LOG_OWNED}/nutritional_values/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('energy', response.json())

    def test_nutritional_values_action_other_user(self):
        self.authenticate('test')
        response = self.client.get(f'{self.url}{LOG_OTHER}/nutritional_values/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
