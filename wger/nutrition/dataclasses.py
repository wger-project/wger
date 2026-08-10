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
from decimal import Decimal
from typing import Optional

# wger
from wger.nutrition.consts import (
    ENERGY_CHECK_MIN_KCAL,
    ENERGY_CHECK_TOLERANCE_ABSOLUTE_KCAL,
    ENERGY_CHECK_TOLERANCE_RELATIVE,
    ENERGY_FACTOR,
)
from wger.nutrition.helpers import (
    change_html_entities_to_human_readable,
    remove_problematic_characters,
)


@dataclass
class WeightUnitData:
    uuid: str
    name: str
    gram: int


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
    common_name: str | None
    brand: str | None
    license_id: int
    license_author: str
    license_title: str
    license_object_url: str
    license_derivative_source_url: str = ''
    license_author_url: str = ''
    is_vegan: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    serving_size_gram: Optional[int] = None
    serving_size_unit: Optional[str] = None
    serving_size_amount: Optional[float] = None
    nutriscore: Optional[str] = None

    def sanity_checks(self):
        if not self.name:
            raise ValueError('Name is empty!')
        self.name = self.name[:200]
        self.brand = self.brand[:200] if self.brand is not None else None
        self.common_name = self.common_name[:200] if self.common_name is not None else None
        self.license_title = self.license_title[:200]

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
        # The dumps are user generated, anything can turn up where a number is
        # expected. Reject it like any other invalid value instead of letting a
        # TypeError escape and abort the whole import run.
        for field in ['energy'] + macros:
            value = getattr(self, field)
            if value is not None and not isinstance(value, (int, float, Decimal)):
                raise ValueError(f'Value for {field} is not a number: {value!r}')

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
                f'Sugar is greater than carbohydrates: '
                f'{self.carbohydrates_sugar} > {self.carbohydrates}'
            )

        # Labels can legally sum to slightly more than 100g per 100g of product because
        # of the per-nutrient measurement tolerances allowed by EU Regulation 1169/2011:
        # https://food.ec.europa.eu/system/files/2016-10/labelling_nutrition-vitamins_minerals-guidance_tolerances_1212_en.pdf
        # The limit of 105 matches the threshold used by Open Food Facts' own data
        # quality check "nutrition-value-total-over-105".
        if self.carbohydrates + self.protein + self.fat > 105:
            raise ValueError('Total of carbohydrates, protein and fat is greater than 105!')

        if self.nutriscore is not None and self.nutriscore not in ('a', 'b', 'c', 'd', 'e'):
            raise ValueError(f'Invalid nutriscore value: {self.nutriscore}')

        # Energy plausibility: the declared energy must roughly match the energy
        # computed from the macronutrients. Fiber counts with 2 kcal/g since it is
        # usually not included in the carbohydrate value. See the comments on the
        # threshold constants in consts.py for the tolerances used.
        energy_computed = (
            self.protein * ENERGY_FACTOR['protein']
            + self.carbohydrates * ENERGY_FACTOR['carbohydrates']
            + self.fat * ENERGY_FACTOR['fat']
            + (self.fiber or 0) * ENERGY_FACTOR['fiber']
        )
        if self.energy > ENERGY_CHECK_MIN_KCAL or energy_computed > ENERGY_CHECK_MIN_KCAL:
            energy_lower = (
                self.energy * (1 - ENERGY_CHECK_TOLERANCE_RELATIVE)
                - ENERGY_CHECK_TOLERANCE_ABSOLUTE_KCAL
            )
            energy_upper = (
                self.energy * (1 + ENERGY_CHECK_TOLERANCE_RELATIVE)
                + ENERGY_CHECK_TOLERANCE_ABSOLUTE_KCAL
            )
            if not (energy_lower <= energy_computed <= energy_upper):
                raise ValueError(
                    f'Energy computed from the macronutrients ({energy_computed:.0f} kcal) '
                    f'does not match the declared energy ({self.energy:.0f} kcal)'
                )

    def dict(self):
        data = asdict(self)
        data.pop('serving_size_gram', None)
        data.pop('serving_size_unit', None)
        data.pop('serving_size_amount', None)
        return data

    def clean_name(self):
        self.name = remove_problematic_characters(self.name)
        self.name = change_html_entities_to_human_readable(self.name)
