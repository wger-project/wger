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
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local
from .trophy import Trophy


class UserTrophy(models.Model):
    """
    Model representing a trophy earned by a user (M2M through table)
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='earned_trophies',
        verbose_name=_('User'),
    )
    """The user who earned the trophy"""

    trophy = models.ForeignKey(
        Trophy,
        on_delete=models.CASCADE,
        related_name='user_trophies',
        verbose_name=_('Trophy'),
    )
    """The trophy that was earned"""

    earned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Earned at'),
        help_text=_('When the trophy was earned'),
    )
    """When the trophy was earned"""

    progress = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name=_('Progress'),
        help_text=_('Progress towards earning the trophy (0-100)'),
    )
    """Progress towards earning the trophy (0-100%)"""

    is_notified = models.BooleanField(
        default=False,
        verbose_name=_('Notified'),
        help_text=_('Whether the user has been notified about earning this trophy'),
    )
    """Whether the user has been notified about this trophy (for future notification system)"""

    class Meta:
        ordering = ['-earned_at']
        verbose_name = _('User trophy')
        verbose_name_plural = _('User trophies')
        unique_together = [['user', 'trophy']]

    def __str__(self):
        return f'{self.user.username} - {self.trophy.name}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self
