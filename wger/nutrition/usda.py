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

# wger
from wger.nutrition.dataclasses import IngredientData
from wger.nutrition.models import Source
from wger.utils.constants import CC_0_LICENSE_ID
from wger.utils.models import AbstractSubmissionModel


def extract_info_from_usda(product_data: dict, language: int) -> IngredientData:
    if not product_data.get('foodNutrients'):
        raise KeyError('Missing key "foodNutrients"')

    energy = 0
    protein = 0
    carbs = 0
    fats = 0
    sugars = 0
    saturated = 0
    fat = 0

    sodium = None
    fibre = None

    for d in product_data['foodNutrients']:
        if not d.get('nutrient'):
            raise KeyError('Missing key "nutrient"')

        nutrient = d.get('nutrient')
        nutrient_id = nutrient.get('id')

        match nutrient_id:
            case 1003:
                protein = float(d.get('amount'))

            case 1004:
                carbs = float(d.get('amount'))

            case 1005:
                fats = float(d.get('amount'))

            case 2048:
                energy = float(d.get('amount'))

            case 1093:
                sodium = float(d.get('amount'))

    if not all([protein, carbs, fats, energy]):
        raise KeyError('Could not extract all nutrition information')

    name = product_data['description']
    if len(name) > 200:
        name = name[:200]

    code = None
    remote_id = product_data['fdcId']
    brand = ''

    # License and author info
    source_name = Source.USDA.value
    source_url = f'https://fdc.nal.usda.gov/'
    author = (
        'U.S. Department of Agriculture, Agricultural Research Service, '
        'Beltsville Human Nutrition Research Center. FoodData Central.'
    )
    object_url = f'https://api.nal.usda.gov/fdc/v1/food/{remote_id}'

    return IngredientData(
        code=code,
        remote_id=remote_id,
        name=name,
        common_name=name,
        language_id=language,
        energy=energy,
        protein=protein,
        carbohydrates=carbs,
        carbohydrates_sugar=sugars,
        fat=fat,
        fat_saturated=saturated,
        fibres=fibre,
        sodium=sodium,
        source_name=source_name,
        source_url=source_url,
        brand=brand,
        status=AbstractSubmissionModel.STATUS_ACCEPTED,
        license_id=CC_0_LICENSE_ID,
        license_author=author,
        license_title=name,
        license_object_url=object_url,
    )
