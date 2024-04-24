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
import importlib
from decimal import Decimal

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.exercises.models import ExerciseBase
from wger.manager.dataclasses import SetConfigData
from wger.manager.models.abstract_config import (
    AbstractChangeConfig,
    OperationChoices,
    StepChoices,
)


class SlotConfig(models.Model):
    """
    Set configuration for an exercise (weight, reps, etc.)
    """

    slot = models.ForeignKey(
        'Slot',
        on_delete=models.CASCADE,
    )

    exercise = models.ForeignKey(
        ExerciseBase,
        on_delete=models.CASCADE,
    )

    repetition_unit = models.ForeignKey(
        RepetitionUnit,
        default=1,
        on_delete=models.CASCADE,
    )
    """
    The repetition unit of a set. This can be e.g. a repetition, a minute, etc.
    """

    repetition_rounding = models.DecimalField(
        decimal_places=2,
        max_digits=4,
        default=1,
    )
    """
    The amount by which the repetitions will be rounded

    Note that this will happen in the UI, and not in the backend
    """

    weight_unit = models.ForeignKey(
        WeightUnit,
        verbose_name=_('Unit'),
        default=1,
        on_delete=models.CASCADE,
    )
    """
    The weight unit of a set. This can be e.g. kg, lb, km/h, etc.
    """

    weight_rounding = models.DecimalField(
        decimal_places=2,
        max_digits=4,
        default=1.25,
    )
    """
    The amount by which the weight will be rounded

    Note that this will happen in the UI, and not in the backend
    """

    order = models.PositiveIntegerField(
        blank=True,
    )

    comment = models.CharField(
        max_length=100,
        blank=True,
    )

    is_dropset = models.BooleanField(
        default=False,
    )

    class_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    """
    The name of a python class that will take care of the change logic.

    If this is set, all other settings will be ignored.
    """

    # Metaclass to set some other properties
    class Meta:
        ordering = [
            'order',
            'id',
        ]

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.slot.day.routine

    @staticmethod
    def calculate_config_value(configs: list[AbstractChangeConfig]) -> Decimal | None:
        if not configs:
            return None

        out = Decimal(0)
        for config in configs:
            if config.replace:
                out = config.value
                continue

            step = config.value if config.step == StepChoices.ABSOLUTE else out * config.value / 100

            if config.operation == OperationChoices.PLUS:
                out += step
            else:
                out -= step

        return out

    def get_config(self, iteration: int) -> SetConfigData:
        # If there is a custom class set, pass all responsibilities to it
        if self.class_name:
            try:
                module = importlib.import_module(
                    f'wger.manager.config_calculations.{self.class_name}'
                )
            except ImportError:
                raise ImportError(f'Class {self.class_name} not found')
            custom_logic = module.SetCalculations(
                iteration=iteration,
                sets_configs=self.setsconfig_set.filter(iteration__lte=iteration),
                weight_configs=self.weightconfig_set.filter(iteration__lte=iteration),
                reps_configs=self.repsconfig_set.filter(iteration__lte=iteration),
                rir_configs=self.rirconfig_set.filter(iteration__lte=iteration),
                rest_configs=self.restconfig_set.filter(iteration__lte=iteration),
                logs=self.workoutlog_set.filter(iteration__lte=iteration),
            )

            return custom_logic.calculate()

        # Calculate the weights normally
        max_iter_weight = 1
        max_iter_reps = 1

        weight = self.get_weight(max_iter_weight)
        reps = self.get_reps(max_iter_reps)

        for i in range(1, iteration + 1):
            # We can't directly do a .get(iteration=i) because there probably isn't one
            # so we simply take the last one, which will be responsible to calculate the
            # weight for the current iteration
            weight_config = self.weightconfig_set.filter(iteration__lte=i).last()
            reps_config = self.repsconfig_set.filter(iteration__lte=i).last()

            if not weight_config or not reps_config:
                break

            elif not weight_config.need_log_to_apply and not reps_config.need_log_to_apply:
                max_iter_weight = i
                max_iter_reps = i

            elif weight_config.need_log_to_apply or reps_config.need_log_to_apply:
                log_data = self.workoutlog_set.filter(iteration=i - 1)

                # If any of the entries in last log is greater than the last config data,
                # proceed. Otherwise, the weight won't change
                for log in log_data:
                    if log.weight >= weight and log.reps >= reps:
                        # weight = log.weight
                        # reps = log.reps

                        max_iter_weight = i
                        max_iter_reps = i

                        # As soon as we find a log, stop
                        break

        weight = self.get_weight(max_iter_weight)
        reps = self.get_reps(max_iter_reps)
        sets = self.get_sets(iteration)

        return SetConfigData(
            sets=sets if sets is not None else 1,
            weight=weight,
            weight_rounding=self.weight_rounding if weight is not None else None,
            weight_unit=self.weight_unit.pk if weight is not None else None,
            reps=reps,
            reps_rounding=self.repetition_rounding if reps is not None else None,
            reps_unit=self.repetition_unit.pk if reps is not None else None,
            rir=self.get_rir(iteration),
            rest=self.get_rest(iteration),
        )

    def get_sets(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(self.setsconfig_set.filter(iteration__lte=iteration))

    def get_weight(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(self.weightconfig_set.filter(iteration__lte=iteration))

    def get_reps(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(self.repsconfig_set.filter(iteration__lte=iteration))

    def get_rir(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(self.rirconfig_set.filter(iteration__lte=iteration))

    def get_rest(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(self.restconfig_set.filter(iteration__lte=iteration))
