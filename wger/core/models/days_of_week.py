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


class DaysOfWeek(models.Model):
    """
    Model for the days of the week

    This model is needed so that 'Day' can have multiple days of the week selected
    """

    day_of_week = models.CharField(max_length=9, verbose_name=_('Day of the week'))

    class Meta:
        """
        Order by day-ID, this is needed for some DBs
        """

        ordering = [
            'pk',
        ]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.day_of_week
