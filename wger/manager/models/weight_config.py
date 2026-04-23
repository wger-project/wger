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

# wger
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from wger.manager.models import AbstractChangeConfig


class WeightConfig(AbstractChangeConfig):
    """
    Configuration model for the weight for a workout set
    """

    rir_baseline = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(3000)],
        help_text=(
            'The weight the user can lift at RiR=0 (i.e. true 1RM or '
            'max effort weight). Used when step=rir_pct to compute the '
            'weekly weight as a percentage of this baseline. '
            'Leave blank to auto-detect from logs (max weight where rir=0).'
        ),
    )


class MaxWeightConfig(AbstractChangeConfig):
    """
    Configuration model for the upper limit of the weight for a workout set
    """

    rir_baseline = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(3000)],
        help_text='The max weight the user can lift at RiR=0.',
    )
