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
from wger.trophies.models import (
    Trophy,
    UserStatistics,
    UserTrophy,
)


class TrophySerializer(serializers.ModelSerializer):
    """
    Serializer for Trophy model.

    Shows trophy information for listing active trophies.
    """

    class Meta:
        model = Trophy
        fields = (
            'id',
            'uuid',
            'name',
            'description',
            'image',
            'trophy_type',
            'is_hidden',
            'is_progressive',
            'order',
        )
        read_only_fields = fields


class UserTrophySerializer(serializers.ModelSerializer):
    """
    Serializer for UserTrophy model.

    Shows user's earned trophies with trophy details.
    """

    trophy = TrophySerializer(read_only=True)

    class Meta:
        model = UserTrophy
        fields = (
            'id',
            'trophy',
            'earned_at',
            'progress',
            'is_notified',
        )
        read_only_fields = fields


class UserStatisticsSerializer(serializers.ModelSerializer):
    """
    Serializer for UserStatistics model.

    Shows user's trophy-related statistics.
    """

    class Meta:
        model = UserStatistics
        fields = (
            'id',
            'total_weight_lifted',
            'total_workouts',
            'current_streak',
            'longest_streak',
            'last_workout_date',
            'earliest_workout_time',
            'latest_workout_time',
            'weekend_workout_streak',
            'last_complete_weekend_date',
            'worked_out_jan_1',
            'last_updated',
        )
        read_only_fields = fields


class TrophyProgressSerializer(serializers.Serializer):
    """
    Serializer for trophy progress information.

    Used for showing progress on all trophies (earned and unearned).
    This is not a ModelSerializer as it aggregates data from multiple sources.
    """

    trophy = TrophySerializer(read_only=True)
    is_earned = serializers.BooleanField()
    earned_at = serializers.DateTimeField(allow_null=True)
    progress = serializers.FloatField()
    current_value = serializers.CharField(allow_null=True)
    target_value = serializers.CharField(allow_null=True)
    progress_display = serializers.CharField(allow_null=True)
