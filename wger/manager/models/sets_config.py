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


class SetsConfig(AbstractChangeConfig):
    """
    Configuration model for the number of sets for a workout set
    """

    value = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    """Sets are always positive integers"""


class MaxSetsConfig(AbstractChangeConfig):
    """
    Configuration model for the maximum number of sets for a workout set
    """

    value = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    """Sets are always positive integers"""
