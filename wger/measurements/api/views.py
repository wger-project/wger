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

# Django
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

# Third Party
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# wger
from wger.measurements.api.filtersets import MeasurementEntryFilterSet
from wger.measurements.api.serializers import (
    MeasurementSerializer,
    UnitSerializer,
)
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.utils.viewsets import WgerOwnerObjectModelViewSet


logger = logging.getLogger(__name__)

def calculate_bmi(user):
    from wger.weight.models import WeightEntry
    
    profile = getattr(user, 'userprofile', None)
    if not profile or not profile.height or profile.height <= 0:
        return []

    # height_sq will be a float
    height_sq = (profile.height / 100) ** 2
    
    weights = WeightEntry.objects.filter(user=user).order_by('date')

    return [
        {
            'id': f'bmi-{w.id}',
            'category': -1,
            'date': w.date,
            # Cast w.weight to float to avoid the Decimal/Float TypeError
            'value': round(float(w.weight) / height_sq, 2),
            'notes': 'Auto-calculated from weight entry'
        }
        for w in weights
    ]

class CategoryViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for measurement units
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UnitSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('id', 'name', 'unit')

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

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(User, 'user')]

    @action(detail=False, methods=['get'])
    def dynamic(self, request):
        """
        Dedicated route for virtual/calculated categories
        URL: /api/v2/measurement-category/dynamic/
        """
        data = [
            {
                'id': -1, 
                'name': 'BMI', 
                'unit': 'kg/m²', 
                'is_dynamic': True
            }
            # easy to append more objects here later
        ]
        return Response(data)


class MeasurementViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for measurements
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MeasurementSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_class = MeasurementEntryFilterSet

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Category, 'category')]

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Measurement.objects.none()

        return Measurement.objects.filter(category__user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Intercept requests for dynamic categories before the filterset blocks them
        """
        category_id = request.query_params.get('category')
        is_dynamic = request.query_params.get('is_dynamic')

        print(request.query_params)
        print("is_dynamic", is_dynamic)

        if category_id == '19':
            bmi_data = calculate_bmi(request.user)
            return Response({
                        "count": len(bmi_data),
                        "next": None,
                        "previous": None,
                        "results": bmi_data
                    })

        return super().list(request, *args, **kwargs)