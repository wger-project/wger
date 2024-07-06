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
from decimal import Decimal

# Django
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.exercises.models import (
    Exercise,
    ExerciseBase,
)
from wger.utils.cache import reset_workout_canonical_form

# Local
from ..consts import RIR_OPTIONS
from .set import Set


class Setting(models.Model):
    """
    Settings for an exercise (weight, reps, etc.)
    """

    set = models.ForeignKey(
        Set,
        verbose_name=_('Sets'),
        on_delete=models.CASCADE,
    )

    exercise_base = models.ForeignKey(
        ExerciseBase,
        verbose_name=_('Exercises'),
        on_delete=models.CASCADE,
    )
    repetition_unit = models.ForeignKey(
        RepetitionUnit,
        verbose_name=_('Unit'),
        default=1,
        on_delete=models.CASCADE,
    )
    """
    The repetition unit of a set. This can be e.g. a repetition, a minute, etc.
    """

    reps = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(600)],
        verbose_name=_('Reps'),
    )
    """
    Amount of repetitions, minutes, etc. for a set.

    Note that since adding the unit field, the name is no longer correct, but is
    kept for compatibility reasons (specially for the REST API).
    """

    weight = models.DecimalField(
        verbose_name=_('Weight'),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(1500))],
    )
    """Planed weight for the repetitions"""

    weight_unit = models.ForeignKey(
        WeightUnit,
        verbose_name=_('Unit'),
        default=1,
        on_delete=models.CASCADE,
    )
    """
    The weight unit of a set. This can be e.g. kg, lb, km/h, etc.
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

    order = models.IntegerField(blank=True, verbose_name=_('Order'))
    comment = models.CharField(max_length=100, blank=True, verbose_name=_('Comment'))

    # Metaclass to set some other properties
    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'setting {self.id} for exercise base {self.exercise_base_id} in set {self.set_id}'

    def save(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_canonical_form(self.set.exerciseday.training_id)

        # If the user selected "Until Failure", do only 1 "repetition",
        # everythin else doesn't make sense.
        if self.repetition_unit == 2:
            self.reps = 1
        super(Setting, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset cache
        """

        reset_workout_canonical_form(self.set.exerciseday.training_id)
        super(Setting, self).delete(*args, **kwargs)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.set.exerciseday.training
