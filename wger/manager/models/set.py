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
import typing

# Django
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.exercises.models import ExerciseBase
from wger.utils.cache import reset_workout_canonical_form
from wger.utils.helpers import normalize_decimal

# Local
from .day import Day


class Set(models.Model):
    """
    Model for a set of exercises
    """

    DEFAULT_SETS = 4
    MAX_SETS = 10

    exerciseday = models.ForeignKey(
        Day,
        verbose_name=_('Exercise day'),
        on_delete=models.CASCADE,
    )
    order = models.IntegerField(
        default=1,
        null=False,
        verbose_name=_('Order'),
    )
    sets = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_SETS)],
        verbose_name=_('Number of sets'),
        default=DEFAULT_SETS,
    )

    comment = models.CharField(max_length=200, verbose_name=_('Comment'), blank=True)

    # Metaclass to set some other properties
    class Meta:
        ordering = [
            'order',
        ]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Set-ID {self.id}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.exerciseday.training

    def save(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        reset_workout_canonical_form(self.exerciseday.training_id)
        super(Set, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        reset_workout_canonical_form(self.exerciseday.training_id)
        super(Set, self).delete(*args, **kwargs)

    @property
    def exercise_bases(self) -> typing.List[ExerciseBase]:
        """Returns the exercises for this set"""
        out = list(
            dict.fromkeys([s.exercise_base for s in self.setting_set.select_related().all()])
        )
        for exercise in out:
            exercise.settings = self.reps_smart_text(exercise)

        return out

    @property
    def compute_settings(self):  # -> typing.List[Setting]:
        """
        Compute the synthetic settings for this set.

        If we have super sets the result will be an interleaved list of
        settings so the result are the exercises that have to be done, in
        order, e.g.:

        * Exercise 1, 10 reps, 50 kg
        * Exercise 2, 8 reps,  10 kg
        * Exercise 1, 10 reps, 50 kg
        * Exercise 2, 8 reps,  10 kg
        """
        setting_lists = []
        for base in self.exercise_bases:
            setting_lists.append(self.computed_settings_exercise(base))

        # Interleave all lists
        return [val for tup in zip(*setting_lists) for val in tup]

    def computed_settings_exercise(self, exercise_base: ExerciseBase):  # -> typing.List[Setting]
        """
        Returns a computed list of settings

        If a set has only one set
        """
        settings = self.setting_set.filter(exercise_base=exercise_base)

        if settings.count() == 0:
            return []
        elif settings.count() == 1:
            setting = settings.first()
            return [setting] * self.sets
        else:
            return list(settings.all())

    def reps_smart_text(self, exercise_base: ExerciseBase):
        """
        "Smart" textual representation

        This is a human representation of the settings, in a way that humans
        would also write: e.g. "8 8 10 10" but "4 x 10" and not "10 10 10 10".
        This helper also takes care to process, hide or show the different repetition
        and weight units as appropriate, e.g. "8 x 2 Plates", "10, 20, 30, ∞"

        :param exercise_base:
        :return setting_text, setting_list:
        """

        def get_rir_representation(setting):
            """
            Returns the representation for the Reps-In-Reserve for a setting
            """

            if setting.rir:
                rir = f'{setting.rir} RiR'
            else:
                rir = ''
            return rir

        def get_reps_reprentation(setting, rep_unit):
            """
            Returns the representation for the repetitions for a setting

            This is basically just to allow for a special representation for the
            "Until Failure" unit
            """
            if setting.repetition_unit_id != 2:
                reps = f'{setting.reps} {rep_unit}'.strip()
            else:
                reps = '∞'
            return reps

        def get_weight_unit_reprentation(setting):
            """
            Returns the representation for the weight unit for a setting

            This is basically just to allow for a special representation for the
            "Repetition" and "Until Failure" unit
            """
            if setting.repetition_unit.id not in (1, 2):
                rep_unit = _(setting.repetition_unit.name)
            else:
                rep_unit = ''
            return rep_unit

        def normalize_weight(setting):
            """
            The weight can be None, or a decimal. In that case, normalize so
            that we don't return e.g. '15.00', but always '15', independently of
            the database used.
            """
            if setting.weight:
                weight = normalize_decimal(setting.weight)
            else:
                weight = setting.weight
            return weight

        def get_setting_text(current_setting, multi=False):
            """Gets the repetition text for a complete setting"""
            rep_unit = get_weight_unit_reprentation(current_setting)
            reps = get_reps_reprentation(current_setting, rep_unit)
            weight_unit = settings[0].weight_unit.name
            weight = normalize_weight(current_setting)
            rir = get_rir_representation(current_setting)
            out = f'{self.sets} × {reps}'.strip() if not multi else reps
            if weight:
                rir_text = f', {rir}' if rir else ''
                out += f' ({weight} {weight_unit}{rir_text})'
            else:
                out += f' ({rir})' if rir else ''

            return out

        settings = self.setting_set.select_related().filter(exercise_base=exercise_base)
        setting_text = ''

        # Only one setting entry, this is a "compact" representation such as e.g.
        # 4x10 or similar
        if len(settings) == 1:
            setting = settings[0]
            setting_text = get_setting_text(setting)

        # There's more than one setting, each set can have a different combination
        # of repetitions, weight, etc. e.g. 10, 8, 8, 12
        elif len(settings) > 1:
            tmp_reps_text = []
            for setting in settings:
                tmp_reps_text.append(get_setting_text(setting, multi=True))

            setting_text = ' – '.join(tmp_reps_text)

        return setting_text
