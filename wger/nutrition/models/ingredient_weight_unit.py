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
import logging

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local
from .ingredient import Ingredient
from .weight_unit import WeightUnit


logger = logging.getLogger(__name__)


class IngredientWeightUnit(models.Model):
    """
    A specific human usable weight unit for an ingredient
    """

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('Ingredient'),
        editable=False,
        on_delete=models.CASCADE,
    )
    unit = models.ForeignKey(
        WeightUnit,
        verbose_name=_('Weight unit'),
        on_delete=models.CASCADE,
    )

    gram = models.IntegerField(verbose_name=_('Amount in grams'))
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        default=1,
        verbose_name=_('Amount'),
        help_text=_('Unit amount, e.g. "1 Cup" or "1/2 spoon"'),
    )

    def get_owner_object(self):
        """
        Weight unit has no owner information
        """
        return None

    def __str__(self):
        """
        Return a more human-readable representation
        """

        return f'{self.amount if self.amount > 1 else ""}{self.unit.name} ({self.gram}g)'
