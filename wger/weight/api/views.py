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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager. If not, see <http://www.gnu.org/licenses/>.

# Third Party
from datetime import timedelta

from django.db.models import Avg, Min, Max
from django.utils.timezone import now

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# wger
from wger.weight.api.filtersets import WeightEntryFilterSet
from wger.weight.api.serializers import WeightEntrySerializer
from wger.weight.models import WeightEntry


class WeightEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoints for body weight tracking.

    Allows users to record body weight over time and retrieve
    aggregated statistics for progress analysis.
    """

    serializer_class = WeightEntrySerializer
    filterset_class = WeightEntryFilterSet
    ordering_fields = "__all__"
    is_private = True

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, "swagger_fake_view", False):
            return WeightEntry.objects.none()

        return WeightEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        Returns summary statistics for the user's weight entries.

        Includes:
        - Total number of entries
        - Current weight
        - Average, minimum and maximum weight
        - Weight change over time
        - Trend direction
        - Average weight for the last 30 days
        """
        qs = self.get_queryset().order_by("date")

        if not qs.exists():
            return Response({
                "message": "No weight entries available"
            })

        first = qs.first().weight
        last = qs.last().weight

        last_30_days = qs.filter(
            date__gte=now().date() - timedelta(days=30)
        )

        data = {
            "total_entries": qs.count(),
            "current_weight": last,
            "average_weight": qs.aggregate(avg=Avg("weight"))["avg"],
            "min_weight": qs.aggregate(min=Min("weight"))["min"],
            "max_weight": qs.aggregate(max=Max("weight"))["max"],
            "weight_change": last - first,
            "trend": (
                "up" if last > first else
                "down" if last < first else
                "stable"
            ),
            "average_last_30_days": last_30_days.aggregate(
                avg=Avg("weight")
            )["avg"],
        }

        return Response(data)
