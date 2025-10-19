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
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.exercises.models import Exercise
from wger.manager.consts import (
    REP_UNIT_REPETITIONS,
    WEIGHT_UNIT_KG,
)
from wger.manager.managers import WorkoutLogManager
from wger.manager.models.session import WorkoutSession
from wger.manager.validators import (
    NullMinValueValidator,
    validate_rir,
)
from wger.utils.cache import reset_workout_log


class WorkoutLog(models.Model):
    """
    A log entry for an exercise
    """

    objects = WorkoutLogManager()

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

    repetitions_unit = models.ForeignKey(
        RepetitionUnit,
        verbose_name=_('Unit'),
        default=REP_UNIT_REPETITIONS,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    """
    The repetition unit of the log. This can be e.g. a repetition, a minute, etc.
    """

    repetitions = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[NullMinValueValidator(0)],
        blank=True,
        null=True,
    )
    """
    Logged amount of repetitions
    """

    repetitions_target = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_('Repetitions'),
        validators=[NullMinValueValidator(0)],
        null=True,
        blank=True,
    )
    """
    Target amount of repetitions
    """

    weight_unit = models.ForeignKey(
        WeightUnit,
        verbose_name=_('Unit'),
        default=WEIGHT_UNIT_KG,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    """
    The weight unit of the log. This can be e.g. kg, lb, km/h, etc.
    """

    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[NullMinValueValidator(0)],
        blank=True,
        null=True,
    )
    """
    Logged amount of weight
    """

    weight_target = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_('Weight'),
        validators=[NullMinValueValidator(0)],
        null=True,
        blank=True,
    )
    """
    Target amount of weight
    """

    rir = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[NullMinValueValidator(0), validate_rir],
        null=True,
        blank=True,
    )
    """
    Reps in Reserve, RiR. The amount of reps that could realistically still be
    done in the set.
    """

    rir_target = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[NullMinValueValidator(0), validate_rir],
        null=True,
        blank=True,
    )
    """
    Target Reps in Reserve
    """

    rest = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    """
    Logged rest time
    """

    rest_target = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    """
    Target rest time
    """

    # Metaclass to set some other properties
    class Meta:
        ordering = ['date', 'repetitions', 'weight']

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Log entry: {self.repetitions} - {self.weight} kg on {self.date}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def clean(self):
        super().clean()
        if self.repetitions is None and self.weight is None:
            raise ValidationError('Both repetitions and weight cannot be null at the same time.')

        if self.repetitions is not None and self.repetitions_unit is None:
            raise ValidationError('Repetitions unit must be present if repetitions have a value.')

        if self.weight is not None and self.weight_unit is None:
            raise ValidationError('Weight unit must be present if weight has a value.')

    def save(self, *args, **kwargs):
        """
        Plumbing
        """
        self.clean()

        # If the routine does not belong to this user, do not save
        if self.routine and self.routine.user != self.user:
            return

        # If there is no session for this date and routine, create one
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
        if self.repetitions_unit == 2:
            self.reps = 1

        # Save to db
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset cache
        """
        try:
            reset_workout_log(
                self.user_id,
                self.session.date.year,
                self.session.date.month,
                self.session.date.day,
            )
        # Catch case when there is no session -> RelatedObjectDoesNotExist
        except WorkoutSession.DoesNotExist:
            pass
        super(WorkoutLog, self).delete(*args, **kwargs)
