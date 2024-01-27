#  This file is part of wger Workout Manager <https://github.com/wger-project>.
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
from typing import Optional

# wger
from wger.nutrition.consts import KJ_PER_KCAL
from wger.nutrition.models import Source
from wger.utils.constants import ODBL_LICENSE_ID
from wger.utils.models import AbstractSubmissionModel


OFF_REQUIRED_TOP_LEVEL = [
    'product_name',
    'code',
    'nutriments',
]
OFF_REQUIRED_NUTRIMENTS = [
    'proteins_100g',
    'carbohydrates_100g',
    'fat_100g',
]


@dataclass
class IngredientData:
    name: str
    language_id: int
    energy: float
    protein: float
    carbohydrates: float
    carbohydrates_sugar: float
    fat: float
    fat_saturated: float
    fibres: Optional[float]
    sodium: Optional[float]
    code: str
    source_name: str
    source_url: str
    common_name: str
    brand: str
    status: str
    license_id: int
    license_author: str
    license_title: str
    license_object_url: str

    def dict(self):
        return asdict(self)


def extract_info_from_off(product_data, language: int):
    if not all(req in product_data for req in OFF_REQUIRED_TOP_LEVEL):
        raise KeyError('Missing required top-level key')

    if not all(req in product_data['nutriments'] for req in OFF_REQUIRED_NUTRIMENTS):
        raise KeyError('Missing required nutrition key')

    # Basics
    name = product_data['product_name']
    if name is None:
        raise KeyError('Product name is None')
    if len(name) > 200:
        name = name[:200]

    common_name = product_data.get('generic_name', '')
    if len(common_name) > 200:
        common_name = common_name[:200]

    # If the energy is not available in kcal, convert from kJ
    if 'energy-kcal_100g' in product_data['nutriments']:
        energy = product_data['nutriments']['energy-kcal_100g']
    elif 'energy-kj_100g' in product_data['nutriments']:
        energy = product_data['nutriments']['energy-kj_100g'] / KJ_PER_KCAL
    else:
        raise KeyError('Energy is not available')

    code = product_data['code']
    protein = product_data['nutriments']['proteins_100g']
    carbs = product_data['nutriments']['carbohydrates_100g']
    sugars = product_data['nutriments'].get('sugars_100g', 0)
    fat = product_data['nutriments']['fat_100g']
    saturated = product_data['nutriments'].get('saturated-fat_100g', 0)

    # these are optional
    sodium = product_data['nutriments'].get('sodium_100g', None)
    fibre = product_data['nutriments'].get('fiber_100g', None)
    brand = product_data.get('brands', None)

    # License and author info
    source_name = Source.OPEN_FOOD_FACTS.value
    source_url = f'https://world.openfoodfacts.org/api/v2/product/{code}.json'
    authors = ', '.join(product_data.get('editors_tags', ['open food facts']))
    object_url = f'https://world.openfoodfacts.org/product/{code}/'

    return IngredientData(
        name=name,
        language_id=language,
        energy=energy,
        protein=protein,
        carbohydrates=carbs,
        carbohydrates_sugar=sugars,
        fat=fat,
        fat_saturated=saturated,
        fibres=fibre,
        sodium=sodium,
        code=code,
        source_name=source_name,
        source_url=source_url,
        common_name=common_name,
        brand=brand,
        status=AbstractSubmissionModel.STATUS_ACCEPTED,
        license_id=ODBL_LICENSE_ID,
        license_author=authors,
        license_title=name,
        license_object_url=object_url,
    )
