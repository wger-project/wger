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

# Standard Library
import datetime

# Django
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local
from .schedule import Schedule
from .workout import Workout


class ScheduleStep(models.Model):
    """
    Model for a step in a workout schedule.

    A step is basically a workout a with a bit of metadata (next and previous
    steps, duration, etc.)
    """

    class Meta:
        """
        Set default ordering
        """

        ordering = [
            'order',
        ]

    schedule = models.ForeignKey(Schedule, verbose_name=_('schedule'), on_delete=models.CASCADE)
    """The schedule is step belongs to"""

    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    """The workout this step manages"""

    duration = models.IntegerField(
        verbose_name=_('Duration'),
        help_text=_('The duration in weeks'),
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(25)],
    )
    """The duration in weeks"""

    order = models.IntegerField(verbose_name=_('Order'), default=1)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.workout

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.workout.name

    def get_dates(self):
        """
        Calculate the start and end date for this step
        """

        steps = self.schedule.schedulestep_set.all()
        start_date = end_date = self.schedule.start_date
        previous = 0

        if not steps:
            return False

        for step in steps:
            start_date += datetime.timedelta(weeks=previous)
            end_date += datetime.timedelta(weeks=step.duration)
            previous = step.duration

            if step == self:
                return start_date, end_date
