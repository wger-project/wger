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
from dataclasses import (
    asdict,
    dataclass,
)
from decimal import Decimal
from typing import Union

# wger
from wger.nutrition.consts import (
    KJ_PER_KCAL,
    MEALITEM_WEIGHT_GRAM,
    MEALITEM_WEIGHT_UNIT,
)


class BaseMealItem:
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
        values = NutritionalValues()

        # Calculate the base weight of the item
        if self.get_unit_type() == MEALITEM_WEIGHT_GRAM:
            item_weight = self.amount
        else:
            item_weight = self.amount * self.weight_unit.amount * self.weight_unit.gram

        values.energy = self.ingredient.energy * item_weight / 100
        values.protein = self.ingredient.protein * item_weight / 100
        values.carbohydrates = self.ingredient.carbohydrates * item_weight / 100
        values.fat = self.ingredient.fat * item_weight / 100

        if self.ingredient.carbohydrates_sugar:
            values.carbohydrates_sugar = self.ingredient.carbohydrates_sugar * item_weight / 100

        if self.ingredient.fat_saturated:
            values.fat_saturated = self.ingredient.fat_saturated * item_weight / 100

        if self.ingredient.fiber:
            values.fiber = self.ingredient.fiber * item_weight / 100

        if self.ingredient.sodium:
            values.sodium = self.ingredient.sodium * item_weight / 100

        # # If necessary, convert weight units
        # if not use_metric:
        #     for key, value in nutritional_info.items():
        #
        #         # Energy is not a weight!
        #         if key == 'energy':
        #             continue
        #
        #         # Everything else, to ounces
        #         nutritional_info[key] = AbstractWeight(value, 'g').oz
        #
        # nutritional_info['energy_kilojoule'] = Decimal(nutritional_info['energy']) * Decimal(4.184)

        # Only 2 decimal places, anything else doesn't make sense
        # for i in nutritional_info:
        #     nutritional_info[i] = Decimal(nutritional_info[i]).quantize(TWOPLACES)

        return values


@dataclass
class NutritionalValues:
    # TODO: replace the Union with | when we drop support for python 3.9

    energy: Union[Decimal, int, float] = 0
    protein: Union[Decimal, int, float] = 0
    carbohydrates: Union[Decimal, int, float] = 0
    carbohydrates_sugar: Union[Decimal, int, float, None] = None
    fat: Union[Decimal, int, float] = 0
    fat_saturated: Union[Decimal, int, float, None] = None
    fiber: Union[Decimal, int, float, None] = None
    sodium: Union[Decimal, int, float, None] = None

    @property
    def energy_kilojoule(self):
        return self.energy * KJ_PER_KCAL

    def __add__(self, other: 'NutritionalValues'):
        """
        Allow adding nutritional values
        """
        return NutritionalValues(
            energy=self.energy + other.energy,
            protein=self.protein + other.protein,
            carbohydrates=self.carbohydrates + other.carbohydrates,
            carbohydrates_sugar=self.carbohydrates_sugar + other.carbohydrates_sugar
            if self.carbohydrates_sugar and other.carbohydrates_sugar
            else self.carbohydrates_sugar or other.carbohydrates_sugar,
            fat=self.fat + other.fat,
            fat_saturated=self.fat_saturated + other.fat_saturated
            if self.fat_saturated and other.fat_saturated
            else self.fat_saturated or other.fat_saturated,
            fiber=self.fiber + other.fiber
            if self.fiber and other.fiber
            else self.fiber or other.fiber,
            sodium=self.sodium + other.sodium
            if self.sodium and other.sodium
            else self.sodium or other.sodium,
        )

    @property
    def to_dict(self):
        return asdict(self)
