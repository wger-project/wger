#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2026 wger Team
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
import enum
import importlib
import logging
from decimal import Decimal
from typing import (
    Callable,
    Dict,
    List,
)

# Django
from django.conf import settings
from django.core.cache import cache
from django.db import models

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
from wger.manager.dataclasses import (
    SetConfigData,
    round_value,
)
from wger.manager.models import WorkoutLog
from wger.manager.models.abstract_config import (
    AbstractChangeConfig,
    OperationChoices,
    StepChoices,
)
from wger.utils.cache import CacheKeyMapper


class ConfigType(enum.Enum):
    WEIGHT = enum.auto()
    MAXWEIGHT = enum.auto()
    REPETITIONS = enum.auto()
    MAXREPETITIONS = enum.auto()
    RIR = enum.auto()
    MAXRIR = enum.auto()
    REST = enum.auto()
    MAXREST = enum.auto()
    SETS = enum.auto()
    MAXSETS = enum.auto()


class ExerciseType(models.TextChoices):
    NORMAL = 'normal'
    DROPSET = 'dropset'
    MYO = 'myo'
    PARTIAL = 'partial'
    FORCED = 'forced'
    TUT = 'tut'
    ISO_HOLD = 'iso'
    JUMP = 'jump'


logger = logging.getLogger(__name__)


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
        default=REP_UNIT_REPETITIONS,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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
        verbose_name='Unit',
        default=WEIGHT_UNIT_KG,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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
        db_index=True,
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

    @property
    def has_progression(self) -> bool:
        """
        Returns true if any config set has more than one entry (is a progression)
        """
        return any(
            len(getattr(self, f'{field}config_set').all()) > 1
            for field in [
                'weight',
                'maxweight',
                'repetitions',
                'maxrepetitions',
                'rir',
                'maxrir',
                'rest',
                'maxrest',
                'sets',
                'maxsets',
            ]
        )

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

            # Auto-calculate order if not provided
            if self.order is None:
                max_order = self.slot.entries.aggregate(models.Max('order'))['order__max']
                self.order = (max_order or 0) + 1

        return super().save(*args, **kwargs)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.slot.day.routine

    def load_all_configs(
        self, iteration: int
    ) -> Dict[str, Dict[str, List[AbstractChangeConfig] | AbstractChangeConfig]]:
        data = {
            'weight': [c for c in self.weightconfig_set.all() if c.iteration <= iteration],
            'maxweight': [c for c in self.maxweightconfig_set.all() if c.iteration <= iteration],
            'repetitions': [
                c for c in self.repetitionsconfig_set.all() if c.iteration <= iteration
            ],
            'maxrepetitions': [
                c for c in self.maxrepetitionsconfig_set.all() if c.iteration <= iteration
            ],
            'rir': [c for c in self.rirconfig_set.all() if c.iteration <= iteration],
            'maxrir': [c for c in self.maxrirconfig_set.all() if c.iteration <= iteration],
            'rest': [c for c in self.restconfig_set.all() if c.iteration <= iteration],
            'maxrest': [c for c in self.maxrestconfig_set.all() if c.iteration <= iteration],
            'sets': [c for c in self.setsconfig_set.all() if c.iteration <= iteration],
            'maxsets': [c for c in self.maxsetsconfig_set.all() if c.iteration <= iteration],
        }
        last_entries = {key: data[key][-1] if data[key] else None for key in data}

        configs = {
            'all': data,
            'last': last_entries,
        }

        return configs

    def get_configuration_entries(
        self, config_type: ConfigType, iteration
    ) -> List[AbstractChangeConfig]:
        configs = {
            ConfigType.WEIGHT: self.weightconfig_set.all(),
            ConfigType.MAXWEIGHT: self.maxweightconfig_set.all(),
            ConfigType.REPETITIONS: self.repetitionsconfig_set.all(),
            ConfigType.MAXREPETITIONS: self.maxrepetitionsconfig_set.all(),
            ConfigType.RIR: self.rirconfig_set.all(),
            ConfigType.MAXRIR: self.maxrirconfig_set.all(),
            ConfigType.REST: self.restconfig_set.all(),
            ConfigType.MAXREST: self.maxrestconfig_set.all(),
            ConfigType.SETS: self.setsconfig_set.all(),
            ConfigType.MAXSETS: self.maxsetsconfig_set.all(),
        }[config_type]

        return [c for c in configs if c.iteration <= iteration]

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

    def get_config_data(self, iteration: int) -> SetConfigData:
        """
        This method calculates the configuration for a given iteration of a slot entry.

        It processes each field (weight, repetitions, rir, rest, sets, etc.) individually
        and for each one it checks if there are any requirements set (minimum values for other
        fields) and checks if they are met by the logs of the previous iterations.

        E.g. the weight could have the requirements of weight and weight. Only if these are
        met, the weight will be increased.
        """

        # If there are no progressions, the value will be always the same
        key = CacheKeyMapper.slot_entry_configs_key(self.pk)
        result = cache.get(key)
        if result and not self.has_progression:
            return result

        logs = list(self.workoutlog_set.all())

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
                repetition_configs=self.repetitionsconfig_set.filter(iteration__lte=iteration),
                max_repetition_configs=self.maxrepetitionsconfig_set.filter(
                    iteration__lte=iteration
                ),
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

        def _requirement_met(log: WorkoutLog, field_name: str) -> bool:
            """Checks if the requirements for a single field are met for this log"""

            log_value = getattr(log, field_name, None)
            if log_value is None:
                return False

            min_value = min_values.get(field_name)
            if min_value is None:
                return False

            return log_value >= min_value

        for i in range(1, iteration + 1):
            configs = self.load_all_configs(i)['last']

            log_data = [
                log for log in logs if log.iteration == i - 1 and log.slot_entry_id == self.id
            ]

            for field, config in configs.items():
                if not config:
                    continue

                requirements = config.requirements_object

                if not requirements:
                    max_iterations[field] = i
                    continue

                # Precompute threshold values for all required fields once per iteration
                # to avoid recalculating them for every log entry.
                min_values: Dict[str, Decimal | None] = {}
                for req_field in requirements.rules:
                    calc_fn: Callable[[int], Decimal | None] | None = getattr(
                        self, f'calculate_{req_field}', None
                    )
                    if not callable(calc_fn):
                        logger.error(
                            f'Missing method calculate_{req_field} on SlotEntry {self.id}',
                        )
                        min_values[req_field] = None
                        continue

                    try:
                        min_values[req_field] = calc_fn(max_iterations[req_field])
                    except Exception as e:
                        logger.error(
                            f'Error during calculate_{req_field} for SlotEntry {self.id}: {e}',
                        )
                        min_values[req_field] = None

                # Field has requirements, check if they are met
                # logger.debug(f'Requirements for {field} in iteration {i}: {requirements.rules}')
                for log in log_data:
                    # If any log satisfies all required fields for the config, the field is ready
                    all_fields_met = all(
                        _requirement_met(log, req_field) for req_field in requirements.rules
                    )
                    if all_fields_met:
                        max_iterations[field] = i
                        break

        sets = self.calculate_sets(max_iterations['sets'])
        max_sets = self.calculate_maxsets(max_iterations['max_sets'])

        weight = self.calculate_weight(max_iterations['weight'])
        max_weight = self.calculate_maxweight(max_iterations['max_weight'])

        repetitions = self.calculate_repetitions(max_iterations['repetitions'])
        max_repetitions = self.calculate_maxrepetitions(max_iterations['max_repetitions'])

        rir = self.calculate_rir(max_iterations['rir'])
        max_rir = self.calculate_maxrir(max_iterations['max_rir'])

        rest = self.calculate_rest(max_iterations['rest'])
        max_rest = self.calculate_maxrest(max_iterations['max_rest'])

        result = SetConfigData(
            slot_entry_id=self.id,
            exercise=self.exercise_id,
            type=str(self.type),
            comment=self.comment,
            sets=sets if sets is not None else 1,
            max_sets=round_value(max_sets, 1),
            weight=round_value(weight, self.weight_rounding),
            max_weight=round_value(max_weight, self.weight_rounding)
            if max_weight and weight and max_weight > weight
            else None,
            weight_rounding=self.weight_rounding if weight is not None else None,
            weight_unit=self.weight_unit_id if weight is not None else None,
            weight_unit_name=self.weight_unit.name
            if weight is not None and self.weight_unit is not None
            else None,
            repetitions=round_value(repetitions, self.repetition_rounding),
            max_repetitions=round_value(max_repetitions, self.repetition_rounding)
            if max_repetitions and repetitions and max_repetitions > repetitions
            else None,
            repetitions_rounding=self.repetition_rounding if repetitions is not None else None,
            repetitions_unit=self.repetition_unit_id if repetitions is not None else None,
            repetitions_unit_name=self.repetition_unit.name
            if repetitions is not None and self.repetition_unit is not None
            else None,
            rir=round_value(rir, 0.5),
            max_rir=round_value(max_rir, 0.5) if max_rir and rir and max_rir > rir else None,
            rest=round_value(rest, 1),
            max_rest=round_value(max_rest, 1) if max_rest and rest and max_rest > rest else None,
        )

        cache.set(
            key,
            result,
            settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'],
        )

        return result

    #
    # Note: don't rename these methods, they are accessed in get_config via getattr
    #
    def calculate_sets(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                self.get_configuration_entries(ConfigType.SETS, iteration),
            )
        )

    def calculate_maxsets(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                self.get_configuration_entries(ConfigType.MAXSETS, iteration),
            )
        )

    def calculate_weight(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                self.get_configuration_entries(ConfigType.WEIGHT, iteration),
            )
        )

    def calculate_maxweight(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                self.get_configuration_entries(ConfigType.MAXWEIGHT, iteration),
            )
        )

    def calculate_repetitions(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                self.get_configuration_entries(ConfigType.REPETITIONS, iteration),
            )
        )

    def calculate_maxrepetitions(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                self.get_configuration_entries(ConfigType.MAXREPETITIONS, iteration),
            )
        )

    def calculate_rir(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                self.get_configuration_entries(ConfigType.RIR, iteration),
            )
        )

    def calculate_maxrir(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                self.get_configuration_entries(ConfigType.MAXRIR, iteration),
            )
        )

    def calculate_rest(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                self.get_configuration_entries(ConfigType.REST, iteration),
            )
        )

    def calculate_maxrest(self, iteration: int) -> Decimal | None:
        return self.calculate_config_value(
            self.duplicate_configs(
                iteration,
                self.get_configuration_entries(ConfigType.MAXREST, iteration),
            )
        )
