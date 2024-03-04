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
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Routine(models.Model):
    """
    Model for a routine
    """

    class Meta:
        ordering = [
            '-creation_date',
        ]

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

    creation_date = models.DateTimeField(
        _('Creation date'),
        auto_now_add=True,
    )

    start = models.DateField(
        _('Start date'),
    )

    end = models.DateField(
        _('End date'),
    )

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
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
            return f'{_("Routine")} ({self.creation_date})'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def clean(self):
        """
        Perform some additional validations
        """

        if self.end and self.start and self.start > self.end:
            raise ValidationError(_('The start time cannot be after the end time.'))
