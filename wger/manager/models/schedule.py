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
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# wger
from wger.manager.managers import ScheduleManager
from wger.utils.fields import Html5DateField


class Schedule(models.Model):
    """
    Model for a workout schedule.

    A schedule is a collection of workous that are done for a certain time.
    E.g. workouts A, B, C, A, B, C, and so on.
    """

    objects = ScheduleManager()
    """Custom manager"""

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        editable=False,
        on_delete=models.CASCADE,
    )
    """
    The user this schedule belongs to. This could be accessed through a step
    that points to a workout, that points to a user, but this is more straight
    forward and performant
    """

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=100,
        help_text=_("Name or short description of the schedule. For example 'Program XYZ'."),
    )
    """Name or short description of the schedule."""

    start_date = Html5DateField(verbose_name=_('Start date'), default=datetime.date.today)
    """The start date of this schedule"""

    is_active = models.BooleanField(
        verbose_name=_('Schedule active'),
        default=True,
        help_text=_(
            'Tick the box if you want to mark this schedule '
            'as your active one (will be shown e.g. on your '
            'dashboard). All other schedules will then be '
            'marked as inactive'
        ),
    )
    """A flag indicating whether the schedule is active (needed for dashboard)"""

    is_loop = models.BooleanField(
        verbose_name=_('Is a loop'),
        default=False,
        help_text=_(
            'Tick the box if you want to repeat the schedules '
            'in a loop (i.e. A, B, C, A, B, C, and so on)'
        ),
    )
    """A flag indicating whether the schedule should act as a loop"""

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def get_absolute_url(self):
        return reverse('manager:schedule:view', kwargs={'pk': self.id})

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def save(self, *args, **kwargs):
        """
        Only one schedule can be marked as active at a time
        """
        if self.is_active:
            Schedule.objects.filter(user=self.user).update(is_active=False)
            self.is_active = True

        super(Schedule, self).save(*args, **kwargs)

    def get_current_scheduled_workout(self):
        """
        Returns the currently active schedule step for a user
        """
        steps = self.schedulestep_set.all()
        start_date = self.start_date
        found = False
        if not steps:
            return False
        while not found:
            for step in steps:
                current_limit = start_date + datetime.timedelta(weeks=step.duration)
                if current_limit >= datetime.date.today():
                    found = True
                    return step
                start_date = current_limit

            # If it's not a loop, there's no workout that matches, return
            if not self.is_loop:
                return False

    def get_end_date(self):
        """
        Calculates the date when the schedule is over or None is the schedule
        is a loop.
        """
        if self.is_loop:
            return None

        end_date = self.start_date
        for step in self.schedulestep_set.all():
            end_date = end_date + datetime.timedelta(weeks=step.duration)
        return end_date
