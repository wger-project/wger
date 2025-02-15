# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
from dataclasses import (
    asdict,
    dataclass,
)
from typing import Optional

# wger
from wger.nutrition.consts import ENERGY_FACTOR


@dataclass
class IngredientData:
    name: str
    remote_id: str
    language_id: int
    energy: float
    protein: float
    carbohydrates: float
    carbohydrates_sugar: Optional[float]
    fat: float
    fat_saturated: Optional[float]
    fiber: Optional[float]
    sodium: Optional[float]
    code: Optional[str]
    source_name: str
    source_url: str
    common_name: str
    brand: str
    license_id: int
    license_author: str
    license_title: str
    license_object_url: str

    def sanity_checks(self):
        if not self.name:
            raise ValueError(f'Name is empty!')
        self.name = self.name[:200]
        self.brand = self.brand[:200]
        self.common_name = self.common_name[:200]

        # Mass checks (not more than 100g of something per 100g of product etc)
        macros = [
            'protein',
            'fat',
            'fat_saturated',
            'carbohydrates',
            'carbohydrates_sugar',
            'sodium',
            'fiber',
        ]
        for macro in macros:
            value = getattr(self, macro)
            if value and value > 100:
                raise ValueError(f'Value for {macro} is greater than 100: {value}')

        if self.fat_saturated and self.fat_saturated > self.fat:
            raise ValueError(
                f'Saturated fat is greater than fat: {self.fat_saturated} > {self.fat}'
            )

        if self.carbohydrates_sugar and self.carbohydrates_sugar > self.carbohydrates:
            raise ValueError(
                f'Sugar is greater than carbohydrates: {self.carbohydrates_sugar} > {self.carbohydrates}'
            )

        if self.carbohydrates + self.protein + self.fat > 100:
            raise ValueError(f'Total of carbohydrates, protein and fat is greater than 100!')

        # Energy approximations
        energy_protein = self.protein * ENERGY_FACTOR['protein']['metric']
        energy_carbohydrates = self.carbohydrates * ENERGY_FACTOR['carbohydrates']['metric']
        energy_fat = self.fat * ENERGY_FACTOR['fat']['metric']
        energy_calculated = energy_protein + energy_carbohydrates + energy_fat

        if energy_fat > self.energy:
            raise ValueError(
                f'Energy calculated from fat is greater than total energy: {energy_fat} > {self.energy}'
            )

        if energy_carbohydrates > self.energy:
            raise ValueError(
                f'Energy calculated from carbohydrates is greater than total energy: {energy_carbohydrates} > {self.energy}'
            )

        if energy_protein > self.energy:
            raise ValueError(
                f'Energy calculated from protein is greater than total energy: {energy_protein} > {self.energy}'
            )

        if energy_calculated > self.energy:
            raise ValueError(
                f'Total energy calculated is greater than energy: {energy_calculated} > {self.energy}'
            )

    def dict(self):
        return asdict(self)
