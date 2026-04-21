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
from rest_framework import serializers

# wger
from wger.exercises.api.serializers import ExerciseInfoSerializer
from wger.favorites.models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer for Favorite model.
    Shows the favorite relationship between user and exercise.
    """

    class Meta:
        model = Favorite
        fields = (
            'id',
            'user',
            'exercise',
            'created',
        )
        read_only_fields = ('user', 'created')


class FavoriteDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Favorite model.
    Includes exercise information for listing favorites.
    """

    exercise = ExerciseInfoSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = (
            'id',
            'exercise',
            'created',
        )
        read_only_fields = fields


class FavoriteToggleSerializer(serializers.Serializer):
    """
    Serializer for toggling favorite status.
    """

    exercise_id = serializers.IntegerField(required=True)


class FavoriteStatusSerializer(serializers.Serializer):
    """
    Serializer for returning favorite status.
    """

    exercise_id = serializers.IntegerField()
    is_favorited = serializers.BooleanField()
