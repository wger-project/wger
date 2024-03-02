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

# Standard Library
import logging

# Third Party
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

# wger
from wger.measurements.api.serializers import (
    MeasurementSerializer,
    UnitSerializer,
)
from wger.measurements.models import (
    Category,
    Measurement,
)


logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for measurement units
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UnitSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ['id', 'name', 'unit']

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Category.objects.none()

        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)


class MeasurementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for measurements
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MeasurementSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = [
        'id',
        'category',
        'date',
        'value',
    ]

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Measurement.objects.none()

        return Measurement.objects.filter(category__user=self.request.user)
