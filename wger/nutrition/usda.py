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


def convert_to_g_per_100g(entry: dict) -> float:
    """
    Convert a nutrient entry to grams per 100g
    """

    nutrient = entry['nutrient']
    amount = float(entry['amount'])

    if nutrient['unitName'] == 'g':
        return amount

    elif nutrient['unitName'] == 'mg':
        return amount / 1000

    else:
        raise ValueError(f'Unknown unit: {nutrient["unitName"]}')


def extract_info_from_usda(product_data: dict, language: int) -> IngredientData:
    if not product_data.get('foodNutrients'):
        raise KeyError('Missing key "foodNutrients"')

    remote_id = str(product_data['fdcId'])
    barcode = None

    energy = None
    protein = None
    carbs = None
    carbs_sugars = None
    fats = None
    fats_saturated = None

    sodium = None
    fibre = None

    brand = product_data.get('brandName', '')

    for nutrient in product_data['foodNutrients']:
        if not nutrient.get('nutrient'):
            raise KeyError('Missing key "nutrient"')

        nutrient_id = nutrient['nutrient']['id']
        match nutrient_id:
            case 1008:
                energy = float(nutrient.get('amount'))  # in kcal

            case 1003:
                protein = convert_to_g_per_100g(nutrient)

            case 1005:
                carbs = convert_to_g_per_100g(nutrient)

            # Total lipid (fat) | Total fat (NLEA)
            case 1004 | 1085:
                fats = convert_to_g_per_100g(nutrient)

            case 1093:
                sodium = convert_to_g_per_100g(nutrient)

            case 1079:
                fibre = convert_to_g_per_100g(nutrient)

    macros = [energy, protein, carbs, fats]
    for value in macros:
        if value is None:
            raise KeyError(f'Could not extract all basic macros: {macros=} {remote_id=}')

    for value in [protein, fats, fats_saturated, carbs, carbs_sugars, sodium, fibre]:
        if value and value > 100:
            raise ValueError(f'Value for macronutrient is greater than 100! {macros=} {remote_id=}')

    name = product_data['description'].title()
    if not name:
        raise ValueError(f'Name is empty! {remote_id=}')
    if len(name) > 200:
        name = name[:200]

    # License and author info
    source_name = Source.USDA.value
    source_url = f'https://fdc.nal.usda.gov/'
    author = (
        'U.S. Department of Agriculture, Agricultural Research Service, '
        'Beltsville Human Nutrition Research Center. FoodData Central.'
    )
    object_url = f'https://fdc.nal.usda.gov/fdc-app.html#/food-details/{remote_id}/nutrients'

    return IngredientData(
        code=barcode,
        remote_id=remote_id,
        name=name,
        common_name=name,
        language_id=language,
        energy=energy,
        protein=protein,
        carbohydrates=carbs,
        carbohydrates_sugar=carbs_sugars,
        fat=fats,
        fat_saturated=fats_saturated,
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
