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
from unittest.mock import patch

# Django
from django.core.cache import cache
from django.urls import reverse

# Third Party
import requests

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.software.views import (
    CACHE_KEY,
    CACHE_TTL_FAILURE,
    CACHE_TTL_SUCCESS,
    GITHUB_API_TIMEOUT,
    GITHUB_API_URL,
    fetch_github_stats,
)


class FetchGithubStatsTestCase(WgerTestCase):
    """
    The landing page must not block on GitHub, and a failed lookup is reused
    for a while instead of being repeated for every visitor.
    """

    def setUp(self):
        super().setUp()
        cache.clear()

    @patch('wger.software.views.requests.get')
    def test_success_uses_a_short_timeout_and_caches_for_a_week(self, mock_get):
        mock_get.return_value.json.return_value = {'stargazers_count': 42}

        with patch('wger.software.views.cache.set', wraps=cache.set) as mock_set:
            result = fetch_github_stats()

        mock_get.assert_called_once_with(GITHUB_API_URL, timeout=GITHUB_API_TIMEOUT)
        self.assertEqual(GITHUB_API_TIMEOUT, 5)
        self.assertEqual(result['nr_stars'], 42)
        self.assertEqual(mock_set.call_args.args[2], CACHE_TTL_SUCCESS)

        mock_get.reset_mock()
        self.assertEqual(fetch_github_stats()['nr_stars'], 42)
        mock_get.assert_not_called()

    @patch('wger.software.views.requests.get')
    def test_timeout_caches_the_fallback_for_one_hour(self, mock_get):
        mock_get.side_effect = requests.Timeout('timed out')

        with patch('wger.software.views.cache.set', wraps=cache.set) as mock_set:
            result = fetch_github_stats()

        self.assertEqual(result['nr_stars'], 1)
        self.assertEqual(mock_set.call_args.args[2], CACHE_TTL_FAILURE)
        self.assertEqual(cache.get(CACHE_KEY)['nr_stars'], 1)

        mock_get.reset_mock()
        self.assertEqual(fetch_github_stats()['nr_stars'], 1)
        mock_get.assert_not_called()

    @patch('wger.software.views.requests.get')
    def test_connection_error_is_not_retried_on_the_next_visit(self, mock_get):
        mock_get.side_effect = requests.ConnectionError('unreachable')

        first = self.client.get(reverse('software:features'))
        second = self.client.get(reverse('software:features'))

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        mock_get.assert_called_once_with(GITHUB_API_URL, timeout=GITHUB_API_TIMEOUT)
