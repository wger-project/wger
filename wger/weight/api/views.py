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



