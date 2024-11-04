# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import datetime
from datetime import timedelta
import logging

# Django
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.weight.models import WeightEntry
from wger.weight.api.views import WeightEntryViewSet

logger = logging.getLogger(__name__)
User = get_user_model()

class WeightEntryViewSetTestCase(WgerTestCase):
    """
    Tests the WeightEntryViewSet filtering logic
    """

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create weight entries for the test user
        self.create_weight_entries()

        # Initialize the APIRequestFactory
        self.factory = APIRequestFactory()

    def create_weight_entries(self):
        """ Helper function to create weight entries for testing. """
        self.entry_8_days = WeightEntry.objects.create(
            weight=79.0, date=datetime.date.today() - timedelta(days=8), user=self.user
        )
        self.entry_30_days = WeightEntry.objects.create(
            weight=81.0, date=datetime.date.today() - timedelta(days=30), user=self.user
        )
        self.entry_31_days = WeightEntry.objects.create(
            weight=84.0, date=datetime.date.today() - timedelta(days=31), user=self.user
        )
        self.entry_184_days = WeightEntry.objects.create(
            weight=78.6, date=datetime.date.today() - timedelta(days=184), user=self.user
        )
        self.entry_183_days = WeightEntry.objects.create(
            weight=78.8, date=datetime.date.today() - timedelta(days=183), user=self.user
        )
        self.entry_365_days = WeightEntry.objects.create(
            weight=82.0, date=datetime.date.today() - timedelta(days=365), user=self.user
        )
        self.entry_366_days = WeightEntry.objects.create(
            weight=87.0, date=datetime.date.today() - timedelta(days=366), user=self.user
        )
        self.entry_500_days = WeightEntry.objects.create(
            weight=86.0, date=datetime.date.today() - timedelta(days=500), user=self.user
        )

    def get_filtered_queryset(self, filter_type):
        """Helper to create a request with the specified filter and get the filtered queryset."""
        wsgi_request = self.factory.get('/api/weightentries/', {'filter': filter_type} if filter_type else {})
        wsgi_request.user = self.user

        # Wrap WSGIRequest in DRF Request to access query_params
        request = Request(wsgi_request)

        # Manually set the request and user to simulate a real request
        viewset = WeightEntryViewSet()
        viewset.request = request
        viewset.request.user = self.user

        return viewset.get_queryset()

    def test_get_weight_entries_with_empty_filter(self):
        """ Test that all weight entries are returned with an empty filter. """
        queryset = self.get_filtered_queryset('')
        self.assertEqual(queryset.count(), 8)

    def test_filter_last_year(self):
        """ Test that only entries from the last year are returned. """
        queryset = self.get_filtered_queryset('lastYear')
        self.assertEqual(queryset.count(), 6)
        self.assertIn(self.entry_8_days, queryset)
        self.assertIn(self.entry_30_days, queryset)
        self.assertIn(self.entry_31_days, queryset)
        self.assertIn(self.entry_183_days, queryset)
        self.assertIn(self.entry_184_days, queryset)
        self.assertIn(self.entry_365_days, queryset)


    def test_filter_last_half_year(self):
        """ Test that only entries from the last 6 months are returned. """
        queryset = self.get_filtered_queryset('lastHalfYear')
        self.assertEqual(queryset.count(), 4)
        self.assertIn(self.entry_8_days, queryset)
        self.assertIn(self.entry_30_days, queryset)
        self.assertIn(self.entry_31_days, queryset)
        self.assertIn(self.entry_183_days, queryset)

    def test_filter_last_month(self):
        """ Test that only entries from the last month are returned. """
        queryset = self.get_filtered_queryset('lastMonth')
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.entry_8_days, queryset)
        self.assertIn(self.entry_30_days, queryset)


    def test_filter_last_week(self):
        """ Test that no entries are returned when filtering by last week. """
        queryset = self.get_filtered_queryset('lastWeek')
        self.assertEqual(queryset.count(), 0)

    def tearDown(self):
        """ Clean up after tests. """
        self.user.delete()
