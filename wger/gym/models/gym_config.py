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
from django.db import models as m
from django.utils.translation import (
    gettext,
    gettext_lazy as _,
)

# wger
from wger.gym.models import Gym


class GymConfig(m.Model):
    """
    Configuration options for a gym
    """

    gym = m.OneToOneField(
        Gym,
        related_name='config',
        editable=False,
        on_delete=m.CASCADE,
    )
    """
    Gym this configuration belongs to
    """

    weeks_inactive = m.PositiveIntegerField(
        verbose_name=_('Reminder of inactive members'),
        help_text=_(
            'Number of weeks since the last time a '
            'user logged his presence to be considered inactive'
        ),
        default=4,
    )
    """
    Reminder of inactive members
    """

    show_name = m.BooleanField(
        verbose_name=_('Show name in header'),
        help_text=_('Show the name of the gym in the site header'),
        default=False,
    )
    """
    Show name of the current user's gym in the header, instead of 'wger'
    """

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return gettext(f'Configuration for {self.gym.name}')

    def get_owner_object(self):
        """
        Config has no user owner
        """
        return None
