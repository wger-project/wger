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
import uuid

# Django
from django.http import Http404

# Third Party
from rest_framework import viewsets

# wger
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.weight.api.filtersets import WeightEntryFilterSet
from wger.weight.api.serializers import (
    SIGNED_LONG_MAX,
    WeightEntrySerializer,
    compatible_weight_entry_id,
)


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

        # Measurement orders by -date, the historic weight endpoint by date.
        # The id breaks ties so that paging through the entries is stable
        return Measurement.body_weight_for(self.request.user).order_by('date', 'id')

    def get_object(self):
        """
        Accept the legacy numeric id as well as the measurement UUID.

        Clients written against the integer primary key, and openScale-sync
        which stores the id as a Java long, address entries by the number this
        endpoint returns. Newer callers can still use the UUID.
        """
        lookup = self.kwargs[self.lookup_url_kwarg or self.lookup_field]
        try:
            uuid.UUID(str(lookup))
        except (ValueError, AttributeError):
            return self.get_object_by_compatible_id(lookup)
        return super().get_object()

    def get_object_by_compatible_id(self, lookup):
        try:
            wanted = int(lookup)
        except (TypeError, ValueError):
            raise Http404
        if wanted < 0 or wanted > SIGNED_LONG_MAX:
            raise Http404

        queryset = self.filter_queryset(self.get_queryset())
        for entry in queryset:
            if compatible_weight_entry_id(entry.id) == wanted:
                self.check_object_permissions(self.request, entry)
                return entry
        raise Http404

    def perform_create(self, serializer):
        """
        Route the new entry into the user's official body-weight category.
        The value is interpreted in the user's preferred weight unit.
        """
        profile = self.request.user.userprofile
        category = Category.get_or_create_body_weight(self.request.user, unit=profile.weight_unit)
        serializer.save(category=category, extra_data={'unit': profile.weight_unit})

    def perform_update(self, serializer):
        """
        A new value is interpreted in the user's current weight unit, updates
        without a value keep the stored unit.

        Only the unit key is replaced, the rest of extra_data is the provenance
        an import left there.
        """
        if 'value' in serializer.validated_data:
            unit = self.request.user.userprofile.weight_unit
            serializer.save(extra_data={**serializer.instance.extra_data, 'unit': unit})
        else:
            serializer.save()
