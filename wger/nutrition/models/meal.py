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
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.utils.constants import TWOPLACES
from wger.utils.fields import Html5TimeField

# Local
from .plan import NutritionPlan


logger = logging.getLogger(__name__)


class Meal(models.Model):
    """
    A meal
    """

    # Metaclass to set some other properties
    class Meta:
        ordering = [
            "time",
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
        return "{0} Meal".format(self.order)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.plan

    def get_nutritional_values(self, use_metric=True):
        """
        Sums the nutrional info of all items in the meal

        :param use_metric Flag that controls the units used
        """
        nutritional_info = {
            'energy': 0,
            'protein': 0,
            'carbohydrates': 0,
            'carbohydrates_sugar': 0,
            'fat': 0,
            'fat_saturated': 0,
            'fibres': 0,
            'sodium': 0
        }

        # Get the calculated values from the meal item and add them
        for item in self.mealitem_set.select_related():

            values = item.get_nutritional_values(use_metric=use_metric)
            for key in nutritional_info.keys():
                nutritional_info[key] += values[key]

        nutritional_info['energy_kilojoule'] = Decimal(nutritional_info['energy']) * Decimal(4.184)

        # Only 2 decimal places, anything else doesn't make sense
        for i in nutritional_info:
            nutritional_info[i] = Decimal(nutritional_info[i]).quantize(TWOPLACES)

        return nutritional_info
