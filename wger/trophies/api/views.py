#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Third Party
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# wger
from wger.trophies.api.filtersets import (
    TrophyFilterSet,
    UserTrophyFilterSet,
)
from wger.trophies.api.serializers import (
    TrophyProgressSerializer,
    TrophySerializer,
    UserStatisticsSerializer,
    UserTrophySerializer,
)
from wger.trophies.models import (
    Trophy,
    UserStatistics,
    UserTrophy,
)
from wger.trophies.services import TrophyService


class TrophyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Trophy objects.

    Returns active trophies. Hidden trophies are excluded unless:
    - The user has earned them, or
    - The user is staff

    list:
    Return a list of active trophies

    retrieve:
    Return a specific trophy by ID
    """

    serializer_class = TrophySerializer
    filterset_class = TrophyFilterSet
    ordering_fields = ['order', 'name', 'trophy_type']
    ordering = ['order', 'name']

    def get_queryset(self):
        """
        Return active trophies, filtering hidden ones appropriately.
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Trophy.objects.none()

        user = self.request.user
        queryset = Trophy.objects.filter(is_active=True)

        # Staff can see all trophies
        if user.is_staff:
            return queryset

        # For regular users, exclude hidden trophies unless earned
        if user.is_authenticated:
            earned_trophy_ids = UserTrophy.objects.filter(user=user).values_list(
                'trophy_id', flat=True
            )
            return queryset.filter(is_hidden=False) | queryset.filter(id__in=earned_trophy_ids)

        # Anonymous users only see non-hidden trophies
        return queryset.filter(is_hidden=False)

    @extend_schema(
        summary="Get trophy progress",
        description="""
        Return all trophies with progress information for the current user.

        For each trophy, returns:
        - Trophy information (id, name, description, type, etc.)
        - Whether the trophy has been earned
        - Earned timestamp (if earned)
        - Progress percentage (0-100)
        - Current and target values (for progressive trophies)

        Hidden trophies are excluded unless earned (or user is staff).
        """,
        responses={
            200: TrophyProgressSerializer(many=True),
        },
    )
    @action(detail=False, methods=['get'])
    def progress(self, request):
        """
        Return all trophies with progress information for the current user.

        For each trophy, returns:
        - Trophy info
        - Whether earned
        - Earned timestamp (if earned)
        - Progress percentage (0-100)
        - Current/target values (for progressive trophies)
        """
        if not request.user.is_authenticated:
            return Response([])

        include_hidden = request.user.is_staff
        progress_data = TrophyService.get_all_trophy_progress(
            request.user,
            include_hidden=include_hidden,
        )

        serializer = TrophyProgressSerializer(progress_data, many=True)
        return Response(serializer.data)


class UserTrophyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for user's earned trophies.

    Returns the current user's earned trophies.

    list:
    Return all earned trophies for the current user

    retrieve:
    Return a specific user trophy by ID
    """

    serializer_class = UserTrophySerializer
    filterset_class = UserTrophyFilterSet
    ordering_fields = ['earned_at', 'trophy__name']
    ordering = ['-earned_at']

    is_private = True

    def get_queryset(self):
        """
        Return only the current user's trophies.
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return UserTrophy.objects.none()

        return UserTrophy.objects.filter(user=self.request.user).select_related('trophy')


class UserStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for user's trophy statistics.

    Returns the current user's trophy-related statistics.

    list:
    Return the current user's statistics

    retrieve:
    Return statistics by ID
    """

    serializer_class = UserStatisticsSerializer
    ordering_fields = '__all__'

    is_private = True

    def get_queryset(self):
        """
        Return only the current user's statistics.
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return UserStatistics.objects.none()

        return UserStatistics.objects.filter(user=self.request.user)
