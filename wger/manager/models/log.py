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
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.exercises.models import ExerciseBase
from wger.utils.cache import reset_workout_log
from wger.utils.fields import Html5DateField

# Local
from ..consts import RIR_OPTIONS
from .session import WorkoutSession
from .workout import Workout


class WorkoutLog(models.Model):
    """
    A log entry for an exercise
    """

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        editable=False,
        on_delete=models.CASCADE,
    )

    exercise_base = models.ForeignKey(
        ExerciseBase,
        verbose_name=_('Exercise'),
        on_delete=models.CASCADE,
    )

    workout = models.ForeignKey(
        Workout,
        verbose_name=_('Workout'),
        on_delete=models.CASCADE,
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

    date = Html5DateField(verbose_name=_('Date'))

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

    def get_workout_session(self, date=None):
        """
        Returns the corresponding workout session

        :return the WorkoutSession object or None if nothing was found
        """
        if not date:
            date = self.date

        try:
            return WorkoutSession.objects.filter(user=self.user).get(date=date)
        except WorkoutSession.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_log(self.user_id, self.date.year, self.date.month, self.date.day)

        # If the user selected "Until Failure", do only 1 "repetition",
        # everythin else doesn't make sense.
        if self.repetition_unit == 2:
            self.reps = 1
        super(WorkoutLog, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_log(self.user_id, self.date.year, self.date.month, self.date.day)
        super(WorkoutLog, self).delete(*args, **kwargs)
