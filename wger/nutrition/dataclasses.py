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

        if self.carbohydrates + self.protein + self.fat > 100:
            raise ValueError(f'Total of carbohydrates, protein and fat is greater than 100!')

    def dict(self):
        return asdict(self)
