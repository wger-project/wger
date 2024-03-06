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
from django.utils.translation import gettext_lazy as _

# wger
from wger.manager.models.set_config import SetConfig


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

    iteration = models.PositiveIntegerField()

    value = models.DecimalField(
        decimal_places=2,
        max_digits=6,
    )

    set_config = models.ForeignKey(
        SetConfig,
        on_delete=models.CASCADE,
    )

    creation_date = models.DateTimeField(
        _('Creation date'),
        auto_now_add=True,
    )

    operation = models.CharField(
        choices=OperationChoices.choices,
        max_length=1,
        default=OperationChoices.PLUS,
        null=True,
    )
    """The operation"""

    trigger = models.CharField(
        choices=TriggerChoices.choices,
        max_length=10,
        default=TriggerChoices.SESSION,
        null=True,
    )
    """When the changes are calculated"""

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

    code = models.CharField(
        max_length=100,
    )
    """
    The name of a python class that will take care of the change logic.

    If this is set, all other settings will be ignored.
    """
