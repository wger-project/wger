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

# wger
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType
from wger.weight.api.filtersets import WeightEntryFilterSet
from wger.weight.api.serializers import WeightEntrySerializer


class WeightEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for weight entry objects
    """

    serializer_class = WeightEntrySerializer

    is_private = True
    ordering_fields = '__all__'
    filterset_class = WeightEntryFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Measurement.objects.none()

        # Measurement orders by -date, the historic weight endpoint by date
        return Measurement.body_weight_for(self.request.user).order_by('date')

    def perform_create(self, serializer):
        """
        Route the new entry into the user's official body-weight category
        """
        category = Category.get_or_create_official(
            self.request.user,
            MetricType.BODY_WEIGHT,
            name='Body weight',
            unit=self.request.user.userprofile.weight_unit,
        )
        serializer.save(category=category)
