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
from decimal import Decimal

# Django
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# wger
from wger.nutrition.helpers import BaseMealItem

# Local
from .ingredient import Ingredient
from .ingredient_weight_unit import IngredientWeightUnit
from .meal import Meal
from .plan import NutritionPlan


class LogItem(BaseMealItem, models.Model):
    """
    An item (component) of a log
    """

    # Metaclass to set some other properties
    class Meta:
        ordering = [
            '-datetime',
        ]

    plan = models.ForeignKey(
        NutritionPlan,
        verbose_name=_('Nutrition plan'),
        on_delete=models.CASCADE,
    )
    """
    The plan this log belongs to
    """

    meal = models.ForeignKey(
        Meal,
        verbose_name=_('Meal'),
        on_delete=models.SET_NULL,
        related_name='log_items',
        blank=True,
        null=True,
    )
    """
    The meal this log belongs to (optional)
    """

    datetime = models.DateTimeField(verbose_name=_('Date and Time (Approx.)'), default=timezone.now)
    """
    Time and date when the log was added
    """

    comment = models.TextField(
        verbose_name=_('Comment'),
        blank=True,
        null=True,
    )
    """
    Comment field, for additional information
    """

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('Ingredient'),
        on_delete=models.CASCADE,
    )
    """
    Ingredient
    """

    weight_unit = models.ForeignKey(
        IngredientWeightUnit,
        verbose_name=_('Weight unit'),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    """
    Weight unit used (grams, slices, etc.)
    """

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        verbose_name=_('Amount'),
        validators=[MinValueValidator(Decimal(1)), MaxValueValidator(Decimal(1000))],
    )
    """
    The amount of units
    """

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Diary entry for {self.datetime}, plan {self.plan.pk}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.plan
