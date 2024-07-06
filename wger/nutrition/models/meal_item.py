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
from decimal import Decimal

# Django
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.nutrition.helpers import BaseMealItem

# Local
from .ingredient import Ingredient
from .ingredient_weight_unit import IngredientWeightUnit
from .meal import Meal


logger = logging.getLogger(__name__)


class MealItem(BaseMealItem, models.Model):
    """
    An item (component) of a meal
    """

    meal = models.ForeignKey(
        Meal,
        verbose_name=_('Nutrition plan'),
        editable=False,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('Ingredient'),
        on_delete=models.CASCADE,
    )
    weight_unit = models.ForeignKey(
        IngredientWeightUnit,
        verbose_name=_('Weight unit'),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    order = models.IntegerField(
        verbose_name=_('Order'),
        blank=True,
        editable=False,
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        verbose_name=_('Amount'),
        validators=[MinValueValidator(Decimal(1)), MaxValueValidator(Decimal(1000))],
    )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'{self.amount}g ingredient {self.ingredient_id}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.meal.plan
