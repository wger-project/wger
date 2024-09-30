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

# wger
from wger.utils.fields import Html5TimeField

# Local
from ..helpers import NutritionalValues
from .plan import NutritionPlan


logger = logging.getLogger(__name__)


class Meal(models.Model):
    """
    A meal
    """

    # Metaclass to set some other properties
    class Meta:
        ordering = [
            'time',
        ]

    plan = models.ForeignKey(
        NutritionPlan,
        verbose_name=_('Nutrition plan'),
        editable=False,
        on_delete=models.CASCADE,
    )
    order = models.IntegerField(
        verbose_name=_('Order'),
        blank=True,
        editable=False,
    )
    time = Html5TimeField(
        null=True,
        blank=True,
        verbose_name=_('Time (approx)'),
    )
    name = models.CharField(
        max_length=25,
        blank=True,
        verbose_name=_('Name'),
        help_text=_(
            'Give meals a textual description / name such as "Breakfast" or "after workout"'
        ),
    )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'{self.order} Meal'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.plan

    def get_nutritional_values(self, use_metric=True):
        """
        Sums the nutritional info of all items in the meal

        :param: use_metric Flag that controls the units used
        """
        nutritional_values = NutritionalValues()

        for item in self.mealitem_set.select_related():
            nutritional_values += item.get_nutritional_values(use_metric=use_metric)

        return nutritional_values
