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
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# wger
from wger.exercises.models import Exercise
from wger.favorites.api.serializers import (
    FavoriteDetailSerializer,
    FavoriteSerializer,
    FavoriteStatusSerializer,
    FavoriteToggleSerializer,
)
from wger.favorites.models import Favorite


class FavoriteViewSet(viewsets.GenericViewSet):
    """
    API endpoint for managing favorite exercises.
    
    All endpoints require authentication.
    
    list:
    Return all favorite exercises for the current user.
    
    toggle:
    Toggle favorite status for an exercise. If favorited, remove it.
    If not favorited, add it.
    
    status:
    Check if an exercise is favorited by the current user.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        """
        Return only the current user's favorites.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user).select_related('exercise')

    @extend_schema(
        summary='List favorite exercises',
        description='Return all favorite exercises for the current user with exercise details.',
        responses={
            200: FavoriteDetailSerializer(many=True),
        },
    )
    def list(self, request):
        """
        List all favorite exercises for the current user.
        """
        favorites = self.get_queryset()
        serializer = FavoriteDetailSerializer(
            favorites,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)

    @extend_schema(
        summary='Toggle favorite status',
        description="""
        Toggle the favorite status for an exercise.
        
        If the exercise is not favorited, it will be added to favorites.
        If the exercise is already favorited, it will be removed from favorites.
        
        Returns:
        - is_favorited: True if the exercise is now favorited, False otherwise
        - was_created: True if a new favorite was created
        """,
        request=FavoriteToggleSerializer,
        responses={
            200: OpenApiResponse(
                description='Favorite status toggled successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'is_favorited': {'type': 'boolean'},
                        'was_created': {'type': 'boolean'},
                    },
                },
            ),
            404: OpenApiResponse(description='Exercise not found'),
        },
    )
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        Toggle favorite status for an exercise.
        """
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        exercise_id = serializer.validated_data['exercise_id']
        
        try:
            exercise = Exercise.objects.get(pk=exercise_id)
        except Exercise.DoesNotExist:
            return Response(
                {'detail': 'Exercise not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        is_favorited, was_created = Favorite.toggle_favorite(request.user, exercise)
        
        return Response({
            'is_favorited': is_favorited,
            'was_created': was_created,
        })

    @extend_schema(
        summary='Check favorite status',
        description='Check if a specific exercise is favorited by the current user.',
        parameters=[
            OpenApiParameter(
                name='exercise_id',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Exercise ID to check',
                required=True,
            ),
        ],
        responses={
            200: FavoriteStatusSerializer,
            404: OpenApiResponse(description='Exercise not found'),
        },
    )
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Check if an exercise is favorited by the current user.
        """
        exercise_id = request.query_params.get('exercise_id')
        
        if not exercise_id:
            return Response(
                {'detail': 'exercise_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            exercise = Exercise.objects.get(pk=int(exercise_id))
        except (Exercise.DoesNotExist, ValueError):
            return Response(
                {'detail': 'Exercise not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        is_favorited = Favorite.is_favorited(request.user, exercise)
        
        return Response({
            'exercise_id': exercise_id,
            'is_favorited': is_favorited,
        })
