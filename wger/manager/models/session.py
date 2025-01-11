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
from django.utils.translation import gettext_lazy as _

# wger
from wger.utils.cache import reset_workout_log
from wger.utils.fields import Html5DateField

# Local
from .workout import Workout


class WorkoutSession(models.Model):
    """
    Model for a workout session
    """

    # Note: values hardcoded in manager.helpers.WorkoutCalendar
    IMPRESSION_BAD = '1'
    IMPRESSION_NEUTRAL = '2'
    IMPRESSION_GOOD = '3'

    IMPRESSION = (
        (IMPRESSION_BAD, _('Bad')),
        (IMPRESSION_NEUTRAL, _('Neutral')),
        (IMPRESSION_GOOD, _('Good')),
    )

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
    )
    """
    The user the workout session belongs to

    See note in weight.models.WeightEntry about why this is not editable=False
    """

    workout = models.ForeignKey(
        Workout,
        verbose_name=_('Workout'),
        on_delete=models.CASCADE,
    )
    """
    The workout the session belongs to
    """

    date = Html5DateField(verbose_name=_('Date'))
    """
    The date the workout session was performed
    """

    notes = models.TextField(
        verbose_name=_('Notes'),
        null=True,
        blank=True,
        help_text=_('Any notes you might want to save about this workout session.'),
    )
    """
    User notes about the workout
    """

    impression = models.CharField(
        verbose_name=_('General impression'),
        max_length=2,
        choices=IMPRESSION,
        default=IMPRESSION_NEUTRAL,
        help_text=_(
            'Your impression about this workout session. Did you exercise as well as you could?'
        ),
    )
    """
    The user's general impression of workout
    """

    time_start = models.TimeField(verbose_name=_('Start time'), blank=True, null=True)
    """
    Time the workout session started
    """

    time_end = models.TimeField(verbose_name=_('Finish time'), blank=True, null=True)
    """
    Time the workout session ended
    """

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'{self.workout} - {self.date}'

    class Meta:
        """
        Set other properties
        """

        ordering = [
            'date',
        ]
        unique_together = ('date', 'user')

    def clean(self):
        """
        Perform some additional validations
        """

        if (not self.time_end and self.time_start) or (self.time_end and not self.time_start):
            raise ValidationError(_('If you enter a time, you must enter both start and end time.'))

        if self.time_end and self.time_start and self.time_start > self.time_end:
            raise ValidationError(_('The start time cannot be after the end time.'))

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def save(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_log(self.user_id, self.date.year, self.date.month)
        super(WorkoutSession, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_log(self.user_id, self.date.year, self.date.month)
        super(WorkoutSession, self).delete(*args, **kwargs)
