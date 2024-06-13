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
from collections import Counter
from typing import List

# Django
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# wger
from wger.manager.dataclasses import WorkoutDayData


class Routine(models.Model):
    """
    Model for a routine
    """

    # objects = WorkoutManager()
    # templates = WorkoutTemplateManager()
    # both = WorkoutAndTemplateManager()

    class Meta:
        ordering = [
            '-created',
        ]

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
    )

    first_day = models.ForeignKey(
        'DayNg',
        on_delete=models.CASCADE,
        null=True,
        related_name='day',
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=50,
        blank=True,
    )

    description = models.TextField(
        verbose_name=_('Description'),
        max_length=1000,
        blank=True,
    )

    # TODO: remove the auto_now_add during migration so we can set this to a custom
    #       value and then set it back to auto_now_add
    created = models.DateTimeField(
        _('Creation date'),
        auto_now_add=True,
    )

    start = models.DateField(
        _('Start date'),
    )

    end = models.DateField(
        _('End date'),
    )

    is_template = models.BooleanField(
        verbose_name=_('Workout template'),
        help_text=_(
            'Marking a workout as a template will freeze it and allow you to make copies of it'
        ),
        default=False,
        null=False,
    )

    is_public = models.BooleanField(
        verbose_name=_('Public template'),
        help_text=_('A public template is available to other users'),
        default=False,
        null=False,
    )

    def get_absolute_url(self):
        """
        Returns the canonical URL to view a workout
        """
        return reverse(
            'manager:routine:view',
            kwargs={'pk': self.id},
        )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        if self.name:
            return self.name
        else:
            return f'Routine {self.id} - {self.created}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def clean(self):
        """Validations"""

        if self.end and self.start and self.start > self.end:
            raise ValidationError(_('The start time cannot be after the end time.'))

    @property
    def day_sequence(self):
        """
        Return a sequence of days.

        Each day object points to the next one in the sequence till it loops back
        """

        out = []
        day = self.first_day
        while day:
            if day in out:
                break
            out.append(day)
            day = day.next_day
        return out

    @property
    def label_dict(self) -> dict[datetime.date, str]:
        out = {}
        labels = self.labels.all()

        for label in labels:
            for i in range(label.start_offset, label.end_offset + 1):
                out[self.start + datetime.timedelta(days=i)] = label.label

        return out

    @property
    def date_sequence(self) -> List[WorkoutDayData]:
        """
        Return a list with specific dates and routine days

        If a day needs logs to continue it will be repeated until the user adds one.
        """

        labels = self.label_dict
        delta = datetime.timedelta(days=1)
        current_date = self.start
        current_day = self.first_day
        counter = Counter()
        skip_til_date = None

        out = []

        if current_day is None:
            return out

        while current_date <= self.end:
            # Fill all days till the end of the week with empty workout days
            if skip_til_date:
                out.append(
                    WorkoutDayData(
                        iteration=None,
                        date=current_date,
                        day=None,
                        label=labels.get(current_date),
                    )
                )
                # current_date += delta
                if current_date == skip_til_date:
                    skip_til_date = None
                continue

            counter[current_day] += 1

            if current_day.last_day_in_week:
                days_til_monday = 7 - current_date.weekday()
                skip_til_date = current_date + datetime.timedelta(days=days_til_monday)

            out.append(
                WorkoutDayData(
                    iteration=counter[current_day],
                    date=current_date,
                    day=current_day,
                    label=labels.get(current_date),
                )
            )

            if current_day.can_proceed(current_date):
                current_day = current_day.next_day

            current_date += delta

        return out

    def current_day(self, date=None) -> WorkoutDayData | None:
        """
        Return the WorkoutDayData for the specified day. If no date is given, return
        the results for "today"
        """
        if date is None:
            date = datetime.date.today()

        for data in self.date_sequence:
            if data.date == date:
                return data

        return None