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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Third Party
from rest_framework import viewsets
from django.utils import timezone
from datetime import timedelta

# wger
from wger.weight.api.serializers import WeightEntrySerializer
from wger.weight.models import WeightEntry


class WeightEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for nutrition plan objects
    """

    serializer_class = WeightEntrySerializer

    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('date', 'weight')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return WeightEntry.objects.none()

        # Start with all user's data
        queryset = WeightEntry.objects.filter(user=self.request.user)

        # Filter data based on filter parameter, if given
        filter_type = self.request.query_params.get('filter', None)

        if filter_type == 'lastYear':
            queryset = queryset.filter(date__gte=timezone.now() - timedelta(days=365))
        elif filter_type == 'lastHalfYear':
            queryset = queryset.filter(date__gte=timezone.now() - timedelta(days=183))
        elif filter_type == 'lastMonth':
            queryset = queryset.filter(date__gte=timezone.now() - timedelta(days=30))
        elif filter_type == 'lastWeek':
            queryset = queryset.filter(date__gte=timezone.now() - timedelta(days=7))
        else:
            pass

        return queryset

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)




# # tests/test_weight_api.py
#
# from django.urls import reverse
# from rest_framework.test import APITestCase
# from rest_framework import status
# from datetime import datetime, timedelta
# from wger.weight.models import WeightEntry
# from django.contrib.auth import get_user_model
#
# User = get_user_model()
#
# class WeightEntryFilterTest(APITestCase):
#     def setUp(self):
#         # Create a test user and some test data
#         self.user = User.objects.create_user(username="testuser", password="password")
#         self.client.force_authenticate(user=self.user)
#
#         # Create weight entries with various dates
#         self.last_week_entry = WeightEntry.objects.create(user=self.user, date=datetime.now() - timedelta(days=7), weight=70)
#         self.last_month_entry = WeightEntry.objects.create(user=self.user, date=datetime.now() - timedelta(days=30), weight=72)
#         self.last_year_entry = WeightEntry.objects.create(user=self.user, date=datetime.now() - timedelta(days=365), weight=75)
#
#     def test_filter_last_week(self):
#         url = reverse('weightentry-list') + '?filter=lastWeek'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]['weight'], self.last_week_entry.weight)
#
#     def test_filter_last_month(self):
#         url = reverse('weightentry-list') + '?filter=lastMonth'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 2)  # Includes last week and last month entries
#
#     def test_filter_last_year(self):
#         url = reverse('weightentry-list') + '?filter=lastYear'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 3)  # Includes all entries in the last year
