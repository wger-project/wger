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

# Django
from django.contrib import admin

# Local
from wger.trophies.models import (
    Trophy,
    UserStatistics,
    UserTrophy,
)


@admin.register(Trophy)
class TrophyAdmin(admin.ModelAdmin):
    """Admin configuration for Trophy model"""

    list_display = (
        'name',
        'trophy_type',
        'checker_class',
        'is_active',
        'is_hidden',
        'is_progressive',
        'order',
    )
    list_filter = ('trophy_type', 'is_active', 'is_hidden', 'is_progressive')
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    readonly_fields = ('uuid', 'created', 'updated')


@admin.register(UserTrophy)
class UserTrophyAdmin(admin.ModelAdmin):
    """Admin configuration for UserTrophy model"""

    list_display = ('user', 'trophy', 'earned_at', 'progress', 'is_notified')
    list_filter = ('trophy', 'is_notified', 'earned_at')
    search_fields = ('user__username', 'trophy__name')
    ordering = ('-earned_at',)
    raw_id_fields = ('user',)


@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin):
    """Admin configuration for UserStatistics model"""

    list_display = (
        'user',
        'total_workouts',
        'total_weight_lifted',
        'current_streak',
        'longest_streak',
        'last_workout_date',
        'last_updated',
    )
    search_fields = ('user__username',)
    ordering = ('-last_updated',)
    raw_id_fields = ('user',)
    readonly_fields = ('last_updated',)
