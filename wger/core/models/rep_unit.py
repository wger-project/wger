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
from django.db import models
from django.utils.translation import gettext_lazy as _


class RepetitionUnit(models.Model):
    """
    Setting unit, used in combination with an amount such as '10 reps', '5 km'
    """

    UNIT_TYPE_REPETITIONS = 'REPETITIONS'
    UNIT_TYPE_TIME = 'TIME'
    UNIT_TYPE_DISTANCE = 'DISTANCE'

    UNIT_TYPE_CHOICES = [
        (UNIT_TYPE_REPETITIONS, _('Repetitions')),
        (UNIT_TYPE_TIME, _('Time')),
        (UNIT_TYPE_DISTANCE, _('Distance')),
    ]

    class Meta:
        """
        Set Meta options
        """

        ordering = [
            'name',
        ]

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    unit_type = models.CharField(
        max_length=20,
        choices=UNIT_TYPE_CHOICES,
        default=UNIT_TYPE_REPETITIONS,
        verbose_name=_('Unit Type'),
        help_text=_('The type of unit (repetitions, time, or distance)'),
    )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    #
    # Own methods
    #
    def get_owner_object(self):
        """
        Unit has no owner information
        """
        return None

    @property
    def is_repetition(self):
        """
        Checks that the repetition unit is a repetition proper

        This is done basically to not litter the code with magic IDs
        """
        return self.id == 1

    @property
    def is_time(self):
        """
        Checks if this unit represents a time-based measurement (seconds, minutes)

        Used by the frontend to determine if a countdown timer should be displayed
        """
        return self.unit_type == self.UNIT_TYPE_TIME

    @property
    def is_distance(self):
        """
        Checks if this unit represents a distance measurement (km, miles)
        """
        return self.unit_type == self.UNIT_TYPE_DISTANCE
