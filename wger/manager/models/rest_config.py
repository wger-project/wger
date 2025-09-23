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
from wger.manager.models import AbstractChangeConfig


class RestConfig(AbstractChangeConfig):
    """
    Configuration model for the rest time for a workout set
    """

    value = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1800)],
    )
    """Rest times are always in seconds, so always positive integers"""


class MaxRestConfig(AbstractChangeConfig):
    """
    Configuration model for the upper limit of the rest time for a workout set
    """

    value = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(600)],
    )
    """Rest times are always in seconds, so always positive integers"""
