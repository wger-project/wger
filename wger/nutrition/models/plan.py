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
import datetime
import logging
from decimal import Decimal

# Django
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# wger
from wger.nutrition.consts import ENERGY_FACTOR
from wger.nutrition.helpers import NutritionalValues
from wger.utils.cache import cache_mapper
from wger.utils.constants import TWOPLACES
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)


class NutritionPlan(models.Model):
    """
    A nutrition plan
    """

    # Metaclass to set some other properties
    class Meta:
        # Order by creation_date, descending (oldest first)
        ordering = [
            '-creation_date',
        ]

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        editable=False,
        on_delete=models.CASCADE,
    )

    creation_date = models.DateField(
        _('Creation date'),
        auto_now_add=True,
    )

    description = models.CharField(
        max_length=80,
        blank=True,
        verbose_name=_('Description'),
        help_text=_(
            'A description of the goal of the plan, e.g. "Gain mass" or "Prepare for summer"'
        ),
    )

    only_logging = models.BooleanField(
        verbose_name='Only logging',
        default=False,
    )
    """Flag to indicate that the nutritional plan will only used for logging"""

    goal_energy = models.IntegerField(null=True, default=None)

    goal_protein = models.IntegerField(null=True, default=None)

    goal_carbohydrates = models.IntegerField(null=True, default=None)

    goal_fiber = models.IntegerField(null=True, default=None)

    goal_fat = models.IntegerField(null=True, default=None)

    has_goal_calories = models.BooleanField(
        verbose_name=_('Use daily calories'),
        default=False,
        help_text=_(
            'Tick the box if you want to mark this '
            'plan as having a goal amount of calories. '
            'You can use the calculator or enter the '
            'value yourself.'
        ),
    )
    """A flag indicating whether the plan has a goal amount of calories"""

    def __str__(self):
        """
        Return a more human-readable representation
        """
        if self.description:
            return self.description
        else:
            return str(_('Nutrition plan'))

    def get_absolute_url(self):
        """
        Returns the canonical URL to view this object
        """
        return reverse('nutrition:plan:view', kwargs={'id': self.id})

    def get_nutritional_values(self):
        """
        Sums the nutritional info of all items in the plan
        """
        nutritional_representation = cache.get(cache_mapper.get_nutrition_cache_by_key(self.pk))
        if not nutritional_representation:
            nutritional_values = NutritionalValues()
            use_metric = self.user.userprofile.use_metric
            unit = 'kg' if use_metric else 'lb'
            result = {
                'total': NutritionalValues(),
                'percent': {'protein': 0, 'carbohydrates': 0, 'fat': 0},
                'per_kg': {'protein': 0, 'carbohydrates': 0, 'fat': 0},
            }

            # Energy
            for meal in self.meal_set.select_related():
                nutritional_values += meal.get_nutritional_values(use_metric=use_metric)
            result['total'] = nutritional_values

            energy = nutritional_values.energy

            # In percent
            if energy:
                result['percent']['protein'] = (
                    nutritional_values.protein * ENERGY_FACTOR['protein'][unit] / energy * 100
                )
                result['percent']['carbohydrates'] = (
                    nutritional_values.carbohydrates
                    * ENERGY_FACTOR['carbohydrates'][unit]
                    / energy
                    * 100
                )
                result['percent']['fat'] = (
                    nutritional_values.fat * ENERGY_FACTOR['fat'][unit] / energy * 100
                )

            # Per body weight
            weight_entry = self.get_closest_weight_entry()
            if weight_entry and weight_entry.weight:
                result['per_kg']['protein'] = nutritional_values.protein / weight_entry.weight
                result['per_kg']['carbohydrates'] = (
                    nutritional_values.carbohydrates / weight_entry.weight
                )
                result['per_kg']['fat'] = nutritional_values.fat / weight_entry.weight

            nutritional_representation = result
            cache.set(cache_mapper.get_nutrition_cache_by_key(self.pk), nutritional_representation)
        return nutritional_representation

    def get_closest_weight_entry(self):
        """
        Returns the closest weight entry for the nutrition plan.
        Returns None if there are no entries.
        """
        target = self.creation_date
        closest_entry_gte = (
            WeightEntry.objects.filter(user=self.user)
            .filter(date__gte=target)
            .order_by('date')
            .first()
        )
        closest_entry_lte = (
            WeightEntry.objects.filter(user=self.user)
            .filter(date__lte=target)
            .order_by('-date')
            .first()
        )
        if closest_entry_gte is None or closest_entry_lte is None:
            return closest_entry_gte or closest_entry_lte
        if abs(closest_entry_gte.date - target) < abs(closest_entry_lte.date - target):
            return closest_entry_gte
        else:
            return closest_entry_lte

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def get_calories_approximation(self):
        """
        Calculates the deviation from the goal calories and the actual
        amount of the current plan
        """

        goal_calories = self.user.userprofile.calories
        actual_calories = self.get_nutritional_values()['total']['energy']

        # Within 3%
        if (actual_calories < goal_calories * 1.03) and (actual_calories > goal_calories * 0.97):
            return 1
        # within 7%
        elif (actual_calories < goal_calories * 1.07) and (actual_calories > goal_calories * 0.93):
            return 2
        # within 10%
        elif (actual_calories < goal_calories * 1.10) and (actual_calories > goal_calories * 0.9):
            return 3
        # even more
        else:
            return 4

    def get_log_entries(self, date=None):
        """
        Convenience function that returns the log entries for a given date
        """
        if not date:
            date = datetime.date.today()

        return self.logitem_set.filter(datetime__date=date).select_related()
