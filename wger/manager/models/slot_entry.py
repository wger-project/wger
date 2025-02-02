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
import copy
import importlib
from decimal import Decimal
from typing import List

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.exercises.models import Exercise
from wger.manager.dataclasses import (
    SetConfigData,
    round_value,
)
from wger.manager.models.abstract_config import (
    AbstractChangeConfig,
    OperationChoices,
    StepChoices,
)


class ExerciseType(models.TextChoices):
    NORMAL = 'normal'
    DROPSET = 'dropset'
    MYO = 'myo'
    PARTIAL = 'partial'
    FORCED = 'forced'
    TUT = 'tut'
    ISO_HOLD = 'iso'
    JUMP = 'jump'


class SlotEntry(models.Model):
    """
    Set configuration for an exercise (weight, reps, etc.)
    """

    slot = models.ForeignKey(
        'Slot',
        on_delete=models.CASCADE,
        related_name='entries',
    )

    exercise = models.ForeignKey(
        Exercise,
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
        default=None,
        null=True,
    )
    """
    The amount by which the repetitions will be rounded
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
        default=None,
        null=True,
    )
    """
    The amount by which the weight will be rounded
    """

    order = models.PositiveIntegerField(
        blank=True,
    )

    comment = models.CharField(
        max_length=100,
        blank=True,
    )

    type = models.CharField(
        choices=ExerciseType.choices,
        max_length=10,
        default=ExerciseType.NORMAL,
        null=False,
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

    config = models.JSONField(
        default=None,
        null=True,
    )
    """JSON configuration field for custom behaviour"""

    # Metaclass to set some other properties
    class Meta:
        ordering = [
            'order',
            'id',
        ]

    def save(self, *args, **kwargs):
        """
        Save the object to the database
        """

        # For new entries add default rounding if available
        if not self.id:
            if not self.repetition_rounding:
                self.repetition_rounding = (
                    self.slot.day.routine.user.userprofile.repetitions_rounding
                )
            if not self.weight_rounding:
                self.weight_rounding = self.slot.day.routine.user.userprofile.weight_rounding
        return super().save(*args, **kwargs)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.slot.day.routine

    @staticmethod
    def calculate_config_value(configs: List[AbstractChangeConfig]) -> Decimal | None:
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

    @staticmethod
    def duplicate_configs(
        iteration: int,
        configs: List[AbstractChangeConfig],
    ) -> List[AbstractChangeConfig]:
        """Duplicates configs according to the "repeat" parameter"""

        out = []
        for config in configs:
            if config.repeat:
                for i in range(config.iteration, iteration + 1):
                    # If there is another config responsible for the iteration, finish here
                    if any(other.iteration == i and other.pk != config.pk for other in configs):
                        break

                    new_config = copy.copy(config)
                    new_config.iteration = i
                    out.append(new_config)
            else:
                out.append(config)

        return out

    def get_config(self, iteration: int) -> SetConfigData:
        """
        This method calculates the configuration for a given iteration of a slot entry.

        It processes each field (weight, repetitions, rir, rest, sets, etc.) individually
        and for each one it checks if there are any requirements set (minimum values for other
        fields) and checks if they are met by the logs of the previous iterations.

        E.g. the weight could have the requirements of weight and weight. Only if these are
        met, the weight will be increased.
        """

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
                max_sets_configs=self.maxsetsconfig_set.filter(iteration__lte=iteration),
                weight_configs=self.weightconfig_set.filter(iteration__lte=iteration),
                max_weight_configs=self.maxweightconfig_set.filter(iteration__lte=iteration),
                reps_configs=self.repetitionsconfig_set.filter(iteration__lte=iteration),
                max_reps_configs=self.maxrepetitionsconfig_set.filter(iteration__lte=iteration),
                rir_configs=self.rirconfig_set.filter(iteration__lte=iteration),
                max_rir_configs=self.maxrirconfig_set.filter(iteration__lte=iteration),
                rest_configs=self.restconfig_set.filter(iteration__lte=iteration),
                max_rest_configs=self.maxrestconfig_set.filter(iteration__lte=iteration),
                logs=self.workoutlog_set.filter(iteration__lte=iteration),
            )

            return custom_logic.calculate()

        max_iterations = {
            'weight': 1,
            'max_weight': 1,
            'repetitions': 1,
            'max_repetitions': 1,
            'rir': 1,
            'max_rir': 1,
            'rest': 1,
            'max_rest': 1,
            'sets': 1,
            'max_sets': 1,
        }

        for i in range(1, iteration + 1):
            configs = {
                'weight': self.weightconfig_set.filter(iteration__lte=i).last(),
                'repetitions': self.repetitionsconfig_set.filter(iteration__lte=i).last(),
                'rir': self.rirconfig_set.filter(iteration__lte=i).last(),
                'rest': self.restconfig_set.filter(iteration__lte=i).last(),
                'sets': self.setsconfig_set.filter(iteration__lte=i).last(),
                'max_sets': self.maxsetsconfig_set.filter(iteration__lte=i).last(),
            }
            log_data = self.workoutlog_set.filter(slot_entry_id=self.id, iteration=i - 1)

            for field, config in configs.items():
                if not config:
                    continue

                if not config.requirements:
                    max_iterations[field] = i
                    continue

                requirements = config.requirements_object

                for log in log_data:
                    all_fields_met = all(
                        getattr(log, req_field) is not None
                        and getattr(log, req_field)
                        >= getattr(self, f'calculate_{req_field}')(max_iterations[req_field])
                        for req_field in requirements.rules
                    )

                    if all_fields_met:
                        max_iterations[field] = i

        sets = self.calculate_sets(max_iterations['sets'])
        max_sets = self.calculate_max_sets(max_iterations['max_sets'])

        weight = self.calculate_weight(max_iterations['weight'])
        max_weight = self.calculate_max_weight(max_iterations['max_weight'])

        repetitions = self.calculate_repetitions(max_iterations['repetitions'])
        max_repetitions = self.calculate_max_repetitions(max_iterations['max_repetitions'])

        rir = self.calculate_rir(max_iterations['rir'])
        max_rir = self.calculate_max_rir(max_iterations['max_rir'])

        rest = self.calculate_rest(max_iterations['rest'])
        max_rest = self.calculate_max_rest(max_iterations['max_rest'])

        return SetConfigData(
            slot_entry_id=self.id,
            exercise=self.exercise.id,
            type=str(self.type),
            comment=self.comment,
            sets=sets if sets is not None else 1,
            max_sets=round_value(max_sets, 1),
            weight=round_value(weight, self.weight_rounding),
            max_weight=round_value(max_weight, self.weight_rounding)
            if max_weight and weight and max_weight > weight
            else None,
            weight_rounding=self.weight_rounding if weight is not None else None,
            # TODO: decide on whether to return None or always the unit
            # weight_unit=self.weight_unit.pk if weight is not None else None,
            weight_unit=self.weight_unit.pk,
            repetitions=round_value(repetitions, self.repetition_rounding),
            max_repetitions=round_value(max_repetitions, self.repetition_rounding)
            if max_repetitions and repetitions and max_repetitions > repetitions
            else None,
            repetitions_rounding=self.repetition_rounding if repetitions is not None else None,
            repetitions_unit=self.repetition_unit.pk,
            # TODO: decide on whether to return None or always the unit
            # reps_unit=self.repetition_unit.pk if reps is not None else None,
            rir=round_value(rir, 0.5),
            max_rir=round_value(max_rir, 0.5) if max_rir and rir and max_rir > rir else None,
            rest=round_value(rest, 1),
            max_rest=round_value(max_rest, 1) if max_rest and rest and max_rest > rest else None,
        )

    #
    # Note: don't rename these methods, they are accessed in get_config via getattr
    #
    def calculate_sets(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                list(self.setsconfig_set.filter(iteration__lte=iteration)),
            )
        )

    def calculate_max_sets(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                list(self.maxsetsconfig_set.filter(iteration__lte=iteration)),
            )
        )

    def calculate_weight(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration, list(self.weightconfig_set.filter(iteration__lte=iteration))
            )
        )

    def calculate_max_weight(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                list(self.maxweightconfig_set.filter(iteration__lte=iteration)),
            )
        )

    def calculate_repetitions(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                list(self.repetitionsconfig_set.filter(iteration__lte=iteration)),
            )
        )

    def calculate_max_repetitions(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                list(self.maxrepetitionsconfig_set.filter(iteration__lte=iteration)),
            )
        )

    def calculate_rir(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                list(self.rirconfig_set.filter(iteration__lte=iteration)),
            )
        )

    def calculate_max_rir(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                list(self.maxrirconfig_set.filter(iteration__lte=iteration)),
            )
        )

    def calculate_rest(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                list(self.restconfig_set.filter(iteration__lte=iteration)),
            )
        )

    def calculate_max_rest(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                list(self.maxrestconfig_set.filter(iteration__lte=iteration)),
            )
        )
