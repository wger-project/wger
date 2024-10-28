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
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.exercises.models import Exercise
from wger.manager.consts import RIR_OPTIONS
from wger.manager.models.session import WorkoutSession
from wger.utils.cache import reset_workout_log


class WorkoutLog(models.Model):
    """
    A log entry for an exercise
    """

    date = models.DateTimeField(
        verbose_name=_('Date'),
        default=datetime.datetime.now,
    )

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        editable=False,
        on_delete=models.CASCADE,
    )

    next_log = models.ForeignKey(
        'self',
        editable=True,
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )
    """
    If this is a log entry for a dropset or similar, this field will contain the
    next log entry in the series
    """

    session = models.ForeignKey(
        'WorkoutSession',
        verbose_name=_('Session'),
        on_delete=models.CASCADE,
        null=True,
        related_name='logs',
    )
    """
    The session this log belongs to.

    If none is given, one will be automatically created on save.
    """

    exercise = models.ForeignKey(
        Exercise,
        verbose_name=_('Exercise'),
        on_delete=models.CASCADE,
    )

    routine = models.ForeignKey(
        'Routine',
        verbose_name=_('Workout'),
        on_delete=models.CASCADE,
        null=True,
    )

    slot_entry = models.ForeignKey(
        'SlotEntry',
        on_delete=models.CASCADE,
        null=True,
    )

    iteration = models.PositiveIntegerField(
        null=True,
    )

    repetition_unit = models.ForeignKey(
        RepetitionUnit,
        verbose_name=_('Unit'),
        default=1,
        on_delete=models.CASCADE,
    )
    """
    The unit of the log. This can be e.g. a repetition, a minute, etc.
    """

    reps = models.IntegerField(
        verbose_name=_('Repetitions'),
        validators=[MinValueValidator(0)],
    )
    """
    Amount of repetitions, minutes, etc.

    Note that since adding the unit field, the name is no longer correct, but is
    kept for compatibility reasons (specially for the REST API).
    """

    weight = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        verbose_name=_('Weight'),
        validators=[MinValueValidator(0)],
    )

    weight_unit = models.ForeignKey(
        WeightUnit,
        verbose_name=_('Unit'),
        default=1,
        on_delete=models.CASCADE,
    )
    """
    The weight unit of the log. This can be e.g. kg, lb, km/h, etc.
    """

    rir = models.CharField(
        verbose_name=_('RiR'),
        max_length=3,
        blank=True,
        null=True,
        choices=RIR_OPTIONS,
    )
    """
    Reps in reserve, RiR. The amount of reps that could realistically still be
    done in the set.
    """

    # Metaclass to set some other properties
    class Meta:
        ordering = ['date', 'reps']

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Log entry: {self.reps} - {self.weight} kg on {self.date}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def save(self, *args, **kwargs):
        """
        Plumbing
        """

        # If the routine does not belong to this user, do not save
        if self.routine and self.routine.user != self.user:
            return

        # If the user of session is not this user, remove foreign key
        if self.session and self.session.user != self.user:
            self.session = None

        # If there is no session for this date and routine, create one
        if not self.session:
            self.session = WorkoutSession.objects.get_or_create(
                user=self.user,
                date=self.date,
                routine=self.routine,
            )[0]

        # Reset cache
        reset_workout_log(
            self.user_id,
            self.session.date.year,
            self.session.date.month,
            self.session.date.day,
        )

        # If the user of next_log is not this user, remove foreign key
        if self.next_log and self.next_log.user != self.user:
            self.next_log = None

        # If the user selected "Until Failure", do only 1 "repetition",
        # anything else doesn't make sense.
        if self.repetition_unit == 2:
            self.reps = 1

        # Save to db
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_log(
            self.user_id,
            self.session.date.year,
            self.session.date.month,
            self.session.date.day,
        )
        super(WorkoutLog, self).delete(*args, **kwargs)
