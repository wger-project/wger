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
from django.db import models


class OperationChoices(models.TextChoices):
    PLUS = '+'
    MINUS = '-'


class TriggerChoices(models.TextChoices):
    SESSION = 'session'
    WEEK = 'week'


class StepChoices(models.TextChoices):
    ABSOLUTE = 'abs'
    PERCENT = 'percent'


class AbstractChangeConfig(models.Model):
    """
    Abstract model for weight configurations
    """

    class Meta:
        abstract = True
        ordering = ['slot_config', 'iteration']
        unique_together = ['slot_config', 'iteration']

    slot_config = models.ForeignKey(
        'SlotConfig',
        on_delete=models.CASCADE,
    )

    iteration = models.PositiveIntegerField()
    """
    The iteration this takes effect on.

    Note that what exactly an iteration is depends on the trigger type so
    at the moment this can be session (so basically a day) or a week.
    """

    trigger = models.CharField(
        choices=TriggerChoices.choices,
        max_length=10,
        default=TriggerChoices.SESSION,
        null=True,
    )
    """When the changes are calculated"""

    value = models.DecimalField(
        decimal_places=2,
        max_digits=6,
    )
    """The actual increment"""

    rounding = models.DecimalField(decimal_places=2, max_digits=4, default=1)
    """
    The amount by which the value will be rounded

    Note that this will happen in the UI, and not in the backend
    """

    operation = models.CharField(
        choices=OperationChoices.choices,
        max_length=1,
        default=OperationChoices.PLUS,
        null=True,
    )
    """The operation"""

    step = models.CharField(
        choices=StepChoices.choices,
        max_length=10,
        default=StepChoices.ABSOLUTE,
        null=True,
    )
    """The step by which the change will happen"""

    replace = models.BooleanField(
        default=False,
    )
    """
    Flag indicating that there is no increase, but that the value will simply
    be replaced with the new one
    """

    need_log_to_apply = models.BooleanField(
        default=False,
    )
    """
    Only apply the change if the user logged the last weight, otherwise
    apply the rules anyway
    """
