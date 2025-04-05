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
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

# wger
from wger.manager.dataclasses import ConfigRequirements


class OperationChoices(models.TextChoices):
    PLUS = '+'
    MINUS = '-'
    REPLACE = 'r'


class StepChoices(models.TextChoices):
    NOT_APPLICABLE = 'na'
    ABSOLUTE = 'abs'
    PERCENT = 'percent'


class AbstractChangeConfig(models.Model):
    """
    Abstract model for weight configurations
    """

    class Meta:
        abstract = True
        ordering = ['slot_entry', 'iteration']
        unique_together = ['slot_entry', 'iteration']

    slot_entry = models.ForeignKey(
        'SlotEntry',
        on_delete=models.CASCADE,
    )

    iteration = models.PositiveIntegerField()
    """
    The iteration this takes effect on.
    """

    value = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        validators=[MinValueValidator(0), MaxValueValidator(3000)],
    )
    """The actual increment"""

    operation = models.CharField(
        choices=OperationChoices.choices,
        max_length=1,
        default=OperationChoices.REPLACE,
    )
    """The operation"""

    step = models.CharField(
        choices=StepChoices.choices,
        max_length=10,
        default=StepChoices.ABSOLUTE,
    )
    """The step by which the change will happen"""

    repeat = models.BooleanField(default=False)
    """
    This setting makes the current rule repeat for subsequent iterations until a
    new rule is defined. For example, if you want to increase the weight by 1kg
    each week, you only need to set this rule once and enable "repeat". The system
    will automatically apply it to every following week until you specify a
    different change.
    """

    requirements = models.JSONField(
        default=None,
        null=True,
    )
    """
    Requirements for the application of this rule as JSON

    Currently supported is only a list of fields that must be met in the logs in
    order to continue.

    See the `ConfigRequirements` class and `validate_requirements` for more
    information on the structure.
    """

    @property
    def replace(self) -> bool:
        """
        Flag indicating that there is no increase, but that the value will simply
        be replaced with the new one
        """
        return self.operation == OperationChoices.REPLACE

    @property
    def requirements_object(self) -> ConfigRequirements | None:
        """
        Get the requirements as an object
        """
        if not self.requirements:
            return None

        return ConfigRequirements(self.requirements)

    def save(self, **kwargs):
        """
        Cleanup some combinations. While these would be ignored in the
        calculations anyway, this makes it cleaner
        """

        # Override values for the first iteration.
        if self.iteration == 1:
            self.operation = OperationChoices.REPLACE

        # Override values for replace
        if self.replace:
            self.step = StepChoices.NOT_APPLICABLE

        super().save(**kwargs)

    def get_owner_object(self):
        """
        Get owner information
        """
        return self.slot_entry.slot.day.routine
