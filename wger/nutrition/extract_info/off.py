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
import re

# wger
from wger.nutrition.consts import KJ_PER_KCAL
from wger.nutrition.dataclasses import IngredientData
from wger.nutrition.models import Source
from wger.utils.constants import ODBL_LICENSE_ID


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

MASS_PATTERN = re.compile(r'(?P<mass>\d+(?:[\.,]\d+)?)\s*(?P<unit>kg|g|mg)\b', re.IGNORECASE)
AMOUNT_AND_UNIT_PATTERN = re.compile(
    r'^\s*(?P<amount>\d+(?:[\.,]\d+)?)\s*(?P<unit>[^\d\(\),;\|][^\(\),;\|]*)$'
)


def _mass_match_to_gram(match: re.Match) -> int | None:
    mass = float(match.group('mass').replace(',', '.'))
    unit = match.group('unit').lower()

    factor = {'kg': 1000, 'g': 1, 'mg': 0.001}.get(unit)
    if factor is None:
        return None

    gram_value = mass * factor
    if gram_value <= 0:
        return None

    return int(round(gram_value))


def extract_serving_size_data(serving_size: str) -> tuple[int | None, str | None, float | None]:
    if not serving_size:
        return None, None, None

    # Parse textual amount/unit even if no explicit mass value is present.
    amount = 1.0
    unit = 'Serving'

    no_parentheses = re.sub(r'\([^\)]*\)', '', serving_size)
    no_mass = MASS_PATTERN.sub('', no_parentheses)
    candidate = re.sub(r'\s+', ' ', no_mass).strip(' ,;-/').strip()

    if candidate:
        parsed = AMOUNT_AND_UNIT_PATTERN.match(candidate)
        if parsed:
            amount = float(parsed.group('amount').replace(',', '.'))
            unit = parsed.group('unit').strip()
        else:
            unit = candidate

    if amount <= 0:
        amount = 1.0

    if not unit:
        unit = 'Serving'

    # Prefer mass values in parenthesis, e.g. "200 ml (206 g)".
    parenthesis_matches = [
        _mass_match_to_gram(match)
        for content in re.findall(r'\(([^\)]*)\)', serving_size)
        for match in MASS_PATTERN.finditer(content)
    ]
    parenthesis_matches = [value for value in parenthesis_matches if value is not None]

    all_matches = [_mass_match_to_gram(match) for match in MASS_PATTERN.finditer(serving_size)]
    all_matches = [value for value in all_matches if value is not None]

    gram = (
        parenthesis_matches[0] if parenthesis_matches else (all_matches[0] if all_matches else None)
    )

    return gram, unit[:200], amount


def extract_info_from_off(product_data: dict, language: int) -> IngredientData:
    if not all(req in product_data for req in OFF_REQUIRED_TOP_LEVEL):
        raise KeyError('Missing required top-level key')

    if not all(req in product_data['nutriments'] for req in OFF_REQUIRED_NUTRIMENTS):
        raise KeyError('Missing required nutrition key')

    # Basics
    name = product_data.get('product_name', '')
    common_name = product_data.get('generic_name', '')

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
    fat = product_data['nutriments']['fat_100g']

    # these are optional
    saturated = product_data['nutriments'].get('saturated-fat_100g', None)
    sodium = product_data['nutriments'].get('sodium_100g', None)
    sugars = product_data['nutriments'].get('sugars_100g', None)
    fiber = product_data['nutriments'].get('fiber_100g', None)
    brand = product_data.get('brands', '')
    serving_size = product_data.get('serving_size', '')

    serving_size_gram, serving_size_unit, serving_size_amount = extract_serving_size_data(
        serving_size
    )

    # Dietary properties from OFF ingredients analysis
    is_vegan = None
    is_vegetarian = None
    analysis_tags = product_data.get('ingredients_analysis_tags', [])
    for tag in analysis_tags:
        if tag == 'en:vegan':
            is_vegan = True
        elif tag == 'en:non-vegan':
            is_vegan = False
        elif tag == 'en:vegan-status-unknown':
            is_vegan = None
        elif tag == 'en:maybe-vegan':
            is_vegan = None

        if tag == 'en:vegetarian':
            is_vegetarian = True
        elif tag == 'en:non-vegetarian':
            is_vegetarian = False
        elif tag == 'en:vegetarian-status-unknown':
            is_vegetarian = None
        elif tag == 'en:maybe-vegetarian':
            is_vegetarian = None

    # Nutri-Score
    nutriscore_value = product_data.get('nutrition_grades', None)
    if nutriscore_value not in ('a', 'b', 'c', 'd', 'e'):
        nutriscore_value = None

    # License and author info
    source_name = Source.OPEN_FOOD_FACTS.value
    source_url = f'https://world.openfoodfacts.org/api/v2/product/{code}.json'
    authors = ', '.join(product_data.get('editors_tags', ['open food facts']))
    object_url = f'https://world.openfoodfacts.org/product/{code}/'

    ingredient_data = IngredientData(
        remote_id=code,
        name=name,
        language_id=language,
        energy=energy,
        protein=protein,
        carbohydrates=carbs,
        carbohydrates_sugar=sugars,
        fat=fat,
        fat_saturated=saturated,
        fiber=fiber,
        sodium=sodium,
        code=code,
        source_name=source_name,
        source_url=source_url,
        common_name=common_name,
        brand=brand,
        license_id=ODBL_LICENSE_ID,
        license_author=authors,
        license_title=name,
        license_object_url=object_url,
        is_vegan=is_vegan,
        is_vegetarian=is_vegetarian,
        serving_size_gram=serving_size_gram,
        serving_size_unit=serving_size_unit,
        serving_size_amount=serving_size_amount,
        nutriscore=nutriscore_value,
    )
    ingredient_data.sanity_checks()
    return ingredient_data
