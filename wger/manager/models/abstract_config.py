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
    """

    value = models.DecimalField(
        decimal_places=2,
        max_digits=6,
    )
    """The actual increment"""

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

    def save(self, **kwargs):
        # Override values for the first iteration. While these would be ignored
        # in the calculations anyway, this is cleaner
        if self.iteration == 1:
            self.replace = True
            self.need_log_to_apply = False
            self.step = None
            self.operation = None
        super().save(**kwargs)

    def get_owner_object(self):
        """
        Config has no owner information
        """
        return self.slot_config.slot.day.routine
