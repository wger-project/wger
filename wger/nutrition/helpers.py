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

# wger
from wger.nutrition.consts import (
    MEALITEM_WEIGHT_GRAM,
    MEALITEM_WEIGHT_UNIT,
)
from wger.utils.constants import TWOPLACES
from wger.utils.units import AbstractWeight


class BaseMealItem(object):
    """
    Base class for an item (component) of a meal or log

    This just provides some common helper functions
    """

    def get_unit_type(self):
        """
        Returns the type of unit used:
        - a value in grams
        - a 'human' unit like 'a cup' or 'a slice'
        """

        if self.weight_unit:
            return MEALITEM_WEIGHT_UNIT
        else:
            return MEALITEM_WEIGHT_GRAM

    def get_nutritional_values(self, use_metric=True):
        """
        Sums the nutritional info for the ingredient in the MealItem

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
        # Calculate the base weight of the item
        if self.get_unit_type() == MEALITEM_WEIGHT_GRAM:
            item_weight = self.amount
        else:
            item_weight = (self.amount * self.weight_unit.amount * self.weight_unit.gram)

        nutritional_info['energy'] += self.ingredient.energy * item_weight / 100
        nutritional_info['protein'] += self.ingredient.protein * item_weight / 100
        nutritional_info['carbohydrates'] += self.ingredient.carbohydrates * item_weight / 100
        nutritional_info['fat'] += self.ingredient.fat * item_weight / 100

        if self.ingredient.carbohydrates_sugar:
            nutritional_info['carbohydrates_sugar'] += \
                self.ingredient.carbohydrates_sugar * item_weight / 100

        if self.ingredient.fat_saturated:
            nutritional_info['fat_saturated'] += self.ingredient.fat_saturated * item_weight / 100

        if self.ingredient.fibres:
            nutritional_info['fibres'] += self.ingredient.fibres * item_weight / 100

        if self.ingredient.sodium:
            nutritional_info['sodium'] += self.ingredient.sodium * item_weight / 100

        # If necessary, convert weight units
        if not use_metric:
            for key, value in nutritional_info.items():

                # Energy is not a weight!
                if key == 'energy':
                    continue

                # Everything else, to ounces
                nutritional_info[key] = AbstractWeight(value, 'g').oz

        nutritional_info['energy_kilojoule'] = Decimal(nutritional_info['energy']) * Decimal(4.184)

        # Only 2 decimal places, anything else doesn't make sense
        for i in nutritional_info:
            nutritional_info[i] = Decimal(nutritional_info[i]).quantize(TWOPLACES)

        return nutritional_info
