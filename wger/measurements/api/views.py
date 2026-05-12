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

def calculate_bmi(user, category_id):
    from wger.weight.models import WeightEntry
    
    profile = getattr(user, 'userprofile', None)
    if not profile or not profile.height or profile.height <= 0:
        return []

    # height_sq will be a float
    height_sq = (profile.height / 100) ** 2
    
    weights = WeightEntry.objects.filter(user=user).order_by('date')

    return [
        {
            'id': w.id, # Use integer IDs so the frontend state manager doesn't complain
            'category': int(category_id), # Link it to the requested category
            'date': w.date.isoformat() if hasattr(w.date, 'isoformat') else w.date,
            'value': round(float(w.weight) / height_sq, 2),
            'notes': 'Auto-calculated from weight entry'
        }
        for w in weights
    ]

# Map the dynamic_type enum to the math function
DYNAMIC_REGISTRY = {
    Category.DynamicType.BMI: calculate_bmi,
    # add squat 1rm later
}

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

    @action(detail=False, methods=['get'], url_path='dynamic-types')
    def dynamic_types(self, request):
        """
        Dedicated route for virtual/calculated categories
        Returns a list of available dynamic calculation types from the model Enum.
        URL: /api/v2/measurement-category/dynamic-types/
        """
        choices = [
            {"value": choice.value, "label": choice.label}
            for choice in Category.DynamicType
        ]
        return Response(choices)


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

        if category_id:
            try:
                # look up the category and check its enum value
                category = Category.objects.get(id=category_id, user=request.user)
                
                if category.dynamic_type != Category.DynamicType.NONE:
                    calc_func = DYNAMIC_REGISTRY.get(category.dynamic_type)
                    
                    if calc_func:
                        # execute the math function and wrap it in the DRF pagination envelope
                        data = calc_func(request.user, category_id)
                        return Response({
                            "count": len(data),
                            "next": None,
                            "previous": None,
                            "results": data
                        })
            except (Category.DoesNotExist, ValueError):
                # fallback to standard behavior
                pass

        return super().list(request, *args, **kwargs)