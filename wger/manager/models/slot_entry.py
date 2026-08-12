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
import importlib
import logging
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import List

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
    REQUIREMENTS_RULES_KEYS,
    WEIGHT_UNIT_KG,
)
from wger.manager.dataclasses import (
    SetConfigData,
    round_value,
)
from wger.manager.models import WorkoutLog
from wger.manager.models.abstract_config import (
    MAX_COMPOUND_RIR,
    MAX_COMPOUND_VALUE,
    AbstractChangeConfig,
    OperationChoices,
    StepChoices,
)
from wger.utils.cache import CacheKeyMapper


class ExerciseType(models.TextChoices):
    """
    Types of exercise (set)

    This list needs to be kept in sync with the react and flutter apps:
    * public/locales/en/translation.json, src/components/WorkoutRoutines/models/SlotEntry.ts and
    * lib/l10n/app_en.arb, lib/models/workouts/slot_entry.dart
    """

    NORMAL = 'normal'
    WARMUP = 'warmup'
    DROPSET = 'dropset'
    MYO = 'myo'
    PARTIAL = 'partial'
    FORCED = 'forced'
    TUT = 'tut'
    ISO_HOLD = 'iso'
    JUMP = 'jump'


logger = logging.getLogger(__name__)


PROGRESSION_FIELDS = [
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
"""Fields with progression configs"""

BASE_FIELD = {
    'maxweight': 'weight',
    'maxrepetitions': 'repetitions',
    'maxrir': 'rir',
    'maxrest': 'rest',
    'maxsets': 'sets',
}
"""Maps max fields to their base field, both advance together"""

FIELD_CAPS = {
    field: MAX_COMPOUND_RIR if field in ('rir', 'maxrir') else MAX_COMPOUND_VALUE
    for field in PROGRESSION_FIELDS
}
"""Caps per field, mirror the limits of the display serializer fields"""


def _apply_config_value(
    value: Decimal | None,
    config: AbstractChangeConfig,
    max_value: Decimal,
) -> Decimal:
    """
    Applies a single config step to the running value.

    ``max_value`` clamps the result so e.g. repeated percent progressions
    can't overflow the display field's ``max_digits``.
    """
    out = value if value is not None else Decimal(0)

    if config.replace:
        out = config.value
    else:
        step = config.value if config.step == StepChoices.ABSOLUTE else out * config.value / 100

        if config.operation == OperationChoices.PLUS:
            out += step
        else:
            out -= step

    # Safety net
    if out > max_value:
        out = max_value

    return out


@dataclass(slots=True)
class _WalkState:
    """
    Walk state of a single progression field.

    ``value`` is the running value after all applied configs, ``active`` the
    config whose run covers the current iteration and ``armed`` a gated
    non-repeating config waiting for a qualifying iteration.

    ``advance`` must run for every field of an iteration before any ``apply``,
    the requirement gates of max fields read the candidate of their base field.
    """

    value: Decimal | None = None
    active: AbstractChangeConfig | None = None
    armed: AbstractChangeConfig | None = None

    def advance(self, config: AbstractChangeConfig | None) -> AbstractChangeConfig | None:
        """
        Moves to the next iteration and returns the config that wants to apply.

        A config owns its own iteration, a repeating config also owns every
        following iteration until another config takes over. A non-repeating
        gated config that couldn't apply yet stays armed until it fires or a
        newer config takes over.
        """
        if config is not None:
            self.active = config
            self.armed = None
            return config

        if self.active is not None and self.active.repeat:
            return self.active

        return self.armed

    def apply(
        self,
        candidate: AbstractChangeConfig,
        is_open: bool,
        max_value: Decimal,
    ) -> None:
        """Applies the candidate or arms it for a later qualifying iteration"""
        if is_open:
            self.value = _apply_config_value(self.value, candidate, max_value)
            self.armed = None
        elif not candidate.repeat:
            self.armed = candidate


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
        Returns true if the calculated config data can change across iterations
        """
        return any(
            config.iteration != 1
            for field in PROGRESSION_FIELDS
            for config in getattr(self, f'{field}config_set').all()
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

    @staticmethod
    def walk_config_values(
        configs: List[AbstractChangeConfig],
        iteration: int,
        max_value: Decimal = MAX_COMPOUND_VALUE,
    ) -> Decimal | None:
        """
        Walks the configs iteration by iteration, without requirement gating,
        and returns the value at the requested iteration.

        The ungated special case of the walk in ``get_config_data``, both
        loops build on ``_WalkState``.
        """
        target = max(iteration, 1)
        by_iteration = {c.iteration: c for c in configs if c.iteration <= target}

        state = _WalkState()
        for i in range(1, target + 1):
            candidate = state.advance(by_iteration.get(i))
            if candidate is not None:
                state.apply(candidate, True, max_value)

        return state.value

    def _display_rounding(self, field: str) -> Decimal | int | None:
        """Rounding applied to a field for display and requirement thresholds"""
        return {
            'weight': self.weight_rounding,
            'repetitions': self.repetition_rounding,
            'rir': Decimal('0.5'),
            'rest': 1,
        }.get(field)

    @staticmethod
    def _requirements_met(requirements, log_data: List[WorkoutLog], thresholds: dict) -> bool:
        """True if any single log reaches the thresholds of all required fields"""

        def rule_met(log: WorkoutLog, rule: str) -> bool:
            log_value = getattr(log, rule, None)
            threshold = thresholds.get(rule)
            return log_value is not None and threshold is not None and log_value >= threshold

        return any(all(rule_met(log, rule) for rule in requirements.rules) for log in log_data)

    def get_config_data(self, iteration: int) -> SetConfigData:
        """
        Calculates the configuration for a given iteration of a slot entry.

        The configs of every field are walked iteration by iteration. Configs
        without requirements apply on their calendar schedule. Configs with
        requirements only apply on iterations where a log of the previous
        iteration reaches the displayed prescription of all required fields,
        earning one application per qualifying iteration.
        """

        # If there are no progressions, the value will be always the same
        key = CacheKeyMapper.slot_entry_configs_key(self.pk)
        result = cache.get(key)
        if result and not self.has_progression:
            return result

        # Defence-in-depth: ignore any log rows that don't belong to the
        # routine's owner. The API ownership check should already prevent
        # cross-user logs from being attached to a slot entry, but this
        # filter ensures progression calculations stay user-scoped.
        logs = list(self.workoutlog_set.filter(user=self.slot.day.routine.user))

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

        target = max(iteration, 1)
        configs_by_field = {
            field: {
                config.iteration: config
                for config in getattr(self, f'{field}config_set').all()
                if config.iteration <= target
            }
            for field in PROGRESSION_FIELDS
        }
        states = {field: _WalkState() for field in PROGRESSION_FIELDS}

        logs_by_iteration = defaultdict(list)
        for log in logs:
            logs_by_iteration[log.iteration].append(log)

        for i in range(1, target + 1):
            # Thresholds are the displayed prescriptions of the previous iteration
            thresholds = {
                rule: round_value(states[rule].value, self._display_rounding(rule))
                for rule in REQUIREMENTS_RULES_KEYS
            }
            log_data = logs_by_iteration.get(i - 1, [])

            # All fields advance first, the gates below read the candidates
            # of their base fields
            candidates = {
                field: states[field].advance(configs_by_field[field].get(i))
                for field in PROGRESSION_FIELDS
            }

            for field in PROGRESSION_FIELDS:
                candidate = candidates[field]
                if candidate is None:
                    continue

                # Min and max configs advance together, gated by the base config
                gate_config = candidate
                base_field = BASE_FIELD.get(field)
                if base_field and configs_by_field[base_field]:
                    gate_config = candidates[base_field] or states[base_field].active or candidate

                requirements = gate_config.requirements_object
                # Iteration 1 is the baseline and always applies
                is_open = (
                    i == 1
                    or not requirements
                    or self._requirements_met(requirements, log_data, thresholds)
                )
                states[field].apply(candidate, is_open, FIELD_CAPS[field])

        sets = states['sets'].value
        max_sets = states['maxsets'].value

        weight = states['weight'].value
        max_weight = states['maxweight'].value

        repetitions = states['repetitions'].value
        max_repetitions = states['maxrepetitions'].value

        rir = states['rir'].value
        max_rir = states['maxrir'].value

        rest = states['rest'].value
        max_rest = states['maxrest'].value

        result = SetConfigData(
            slot_entry_id=self.id,
            exercise=self.exercise_id,
            type=str(self.type),
            comment=self.comment,
            sets=sets if sets is not None else 1,
            max_sets=round_value(max_sets, 1),
            weight=round_value(weight, self._display_rounding('weight')),
            max_weight=round_value(max_weight, self._display_rounding('weight'))
            if max_weight and weight and max_weight > weight
            else None,
            weight_rounding=self.weight_rounding if weight is not None else None,
            weight_unit=self.weight_unit_id if weight is not None else None,
            weight_unit_name=self.weight_unit.name
            if weight is not None and self.weight_unit is not None
            else None,
            repetitions=round_value(repetitions, self._display_rounding('repetitions')),
            max_repetitions=round_value(max_repetitions, self._display_rounding('repetitions'))
            if max_repetitions and repetitions and max_repetitions > repetitions
            else None,
            repetitions_rounding=self.repetition_rounding if repetitions is not None else None,
            repetitions_unit=self.repetition_unit_id if repetitions is not None else None,
            repetitions_unit_name=self.repetition_unit.name
            if repetitions is not None and self.repetition_unit is not None
            else None,
            rir=round_value(rir, self._display_rounding('rir')),
            max_rir=round_value(max_rir, self._display_rounding('rir'))
            if max_rir and rir and max_rir > rir
            else None,
            rest=round_value(rest, self._display_rounding('rest')),
            max_rest=round_value(max_rest, self._display_rounding('rest'))
            if max_rest and rest and max_rest > rest
            else None,
        )

        cache.set(
            key,
            result,
            settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'],
        )

        return result
