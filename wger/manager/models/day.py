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
from typing import List

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import DaysOfWeek
from wger.manager.dataclasses import SetData


class DayNg(models.Model):
    """
    Model for a training day
    """

    routine = models.ForeignKey(
        'Routine',
        verbose_name=_('Routine'),
        on_delete=models.CASCADE,
    )

    next_day = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=20,
        verbose_name=_('Description'),
    )

    description = models.CharField(
        max_length=250,
        verbose_name=_('Description'),
    )

    is_rest = models.BooleanField(
        default=False,
    )
    """
    Flag indicating that this day is a rest day.

    Rest days have no exercises
    """

    need_logs_to_advance = models.BooleanField(
        default=False,
    )
    """
    Needs logs to advance to the next day
    """

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.description

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.routine

    def can_proceed(self, date: datetime.date) -> bool:
        """
        Checks whether the user can proceed to the next day in the sequence

        This is possible if
        - the day doesn't require logs
        - the day requires logs, and they exist
        - the date is in the future (used e.g. for calendars where we assume we will proceed)
        """
        if (
            not self.need_logs_to_advance
            or self.workoutsession_set.filter(date=date).exists()
            or date > datetime.date.today()
        ):
            return True

        return False

    def get_sets(self, iteration: int) -> List[SetData]:
        """
        Return the sets for this day
        """
        return [SetData(set=s, exercise_data=s.set_data(iteration)) for s in self.setng_set.all()]


class Day(models.Model):
    """
    Model for a training day
    """

    training = models.ForeignKey(
        'Workout',
        verbose_name=_('Workout'),
        on_delete=models.CASCADE,
    )

    description = models.CharField(
        max_length=100,
        verbose_name=_('Description'),
        help_text=_(
            'A description of what is done on this day (e.g. '
            '"Pull day") or what body parts are trained (e.g. '
            '"Arms and abs")'
        ),
    )
    day = models.ManyToManyField(DaysOfWeek, verbose_name=_('Day'))

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.description

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.training

    @property
    def days_txt(self):
        return ', '.join([str(_(i.day_of_week)) for i in self.day.all()])

    @property
    def get_first_day_id(self):
        """
        Return the PK of the first day of the week, this is used in the template
        to order the days in the template
        """
        return self.day.all()[0].pk
