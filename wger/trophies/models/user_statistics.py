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
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserStatistics(models.Model):
    """
    Denormalized statistics table for trophy calculations.
    This table is updated incrementally as users log workouts to avoid
    expensive recalculations every time a trophy is evaluated.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='trophy_statistics',
        verbose_name=_('User'),
    )
    """The user these statistics belong to"""

    total_weight_lifted = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total weight lifted'),
        help_text=_('Cumulative weight lifted in kg'),
    )
    """Total cumulative weight lifted in kg"""

    total_workouts = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total workouts'),
        help_text=_('Total number of workout sessions completed'),
    )
    """Total number of workout sessions completed"""

    current_streak = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Current streak'),
        help_text=_('Current consecutive days with workouts'),
    )
    """Current consecutive workout streak in days"""

    longest_streak = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Longest streak'),
        help_text=_('Longest consecutive days with workouts'),
    )
    """Longest consecutive workout streak ever achieved"""

    last_workout_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Last workout date'),
        help_text=_('Date of the most recent workout'),
    )
    """Date of the most recent workout"""

    earliest_workout_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('Earliest workout time'),
        help_text=_('Earliest time a workout was started'),
    )
    """Earliest time a workout was ever started"""

    latest_workout_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('Latest workout time'),
        help_text=_('Latest time a workout was started'),
    )
    """Latest time a workout was ever started"""

    weekend_workout_streak = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Weekend workout streak'),
        help_text=_('Consecutive weekends with workouts on both Saturday and Sunday'),
    )
    """Consecutive weekends with workouts on both Saturday and Sunday"""

    last_complete_weekend_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Last complete weekend date'),
        help_text=_('Date of the last Saturday where both Sat and Sun had workouts'),
    )
    """Used for tracking consecutive weekend workouts"""

    last_inactive_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Last inactive date'),
        help_text=_('Last date before the current activity period began'),
    )
    """Used for Phoenix trophy - tracks when user was last inactive"""

    worked_out_jan_1 = models.BooleanField(
        default=False,
        verbose_name=_('Worked out on January 1st'),
        help_text=_('Whether user has ever worked out on January 1st'),
    )
    """Flag for New Year, New Me trophy"""

    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last updated'),
    )
    """When these statistics were last updated"""

    class Meta:
        verbose_name = _('User statistics')
        verbose_name_plural = _('User statistics')

    def __str__(self):
        return f'Statistics for {self.user.username}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self
