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
import math
import re
from decimal import Decimal

# Django
from django.utils import translation
from django.utils.translation import gettext

# wger
from wger.nutrition.consts import KJ_PER_KCAL
from wger.nutrition.dataclasses import IngredientData
from wger.nutrition.models import Source
from wger.utils.constants import ODBL_LICENSE_ID


OFF_REQUIRED_TOP_LEVEL = [
    'code',
    'nutriments',
]
OFF_REQUIRED_NUTRIMENTS = [
    'proteins_100g',
    'carbohydrates_100g',
    'fat_100g',
]
# Avoid magnifying rounding errors in very small servings, as OFF does when
# aggregating nutrition data to 100 g.
MIN_SERVING_MASS_GRAMS = 5

MASS_PATTERN = re.compile(r'(?P<mass>\d+(?:[\.,]\d+)?)\s*(?P<unit>kg|g|mg)\b', re.IGNORECASE)
# Nutrient conversion must not mistake part of a negative, fraction or
# scientific notation for a positive weight. Keep display-label parsing as-is.
NUTRIENT_MASS_PATTERN = re.compile(
    r'(?<![\w.,+/\-\u2212])(?P<mass>[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+))\s*'
    r'(?P<unit>kg|g|mg)\b',
    re.IGNORECASE,
)
AMOUNT_AND_UNIT_PATTERN = re.compile(
    r'^\s*(?P<amount>\d+(?:[\.,]\d+)?)\s*(?P<unit>[^\d\(\),;\|][^\(\),;\|]*)$'
)


def _mass_match_to_gram(match: re.Match) -> float | None:
    mass = float(match.group('mass').replace(',', '.'))
    unit = match.group('unit').lower()

    factor = {'kg': 1000, 'g': 1, 'mg': 0.001}.get(unit)
    if factor is None:
        return None

    gram_value = mass * factor
    if not math.isfinite(gram_value) or gram_value <= 0:
        return None

    return gram_value


def _serving_mass_in_grams(serving_size: str, pattern: re.Pattern = MASS_PATTERN) -> float | None:
    # Prefer the explicit mass in parentheses, e.g. "200 ml (206 g)".
    for text in [*re.findall(r'\(([^\)]*)\)', serving_size), serving_size]:
        for match in pattern.finditer(text):
            if (mass := _mass_match_to_gram(match)) is not None:
                return mass
    return None


def _serving_weight_for_nutrients(product_data: dict) -> float | None:
    unit = product_data.get('serving_quantity_unit')
    if unit == 'g':
        if isinstance(product_data.get('serving_quantity'), bool):
            return None
        try:
            mass = float(product_data.get('serving_quantity'))
        except (TypeError, ValueError, OverflowError):
            return None
        return mass if math.isfinite(mass) and mass > 0 else None

    if unit and unit != 'ml':
        return None

    # Never assume ml are grams. An explicit mass in a legacy label or alongside
    # a volume ("200 ml (206 g)") can still be used, without rounding fractions.
    return _serving_mass_in_grams(product_data.get('serving_size') or '', NUTRIENT_MASS_PATTERN)


def _nutriments_with_serving_fallback(product_data: dict) -> dict:
    nutriments = product_data['nutriments'].copy()
    nutrients = ['proteins', 'carbohydrates', 'fat', 'sugars', 'saturated-fat', 'sodium', 'fiber']

    # Existing per-100g energy, including kJ, wins over any per-serving energy.
    if all(nutriments.get(f'{name}_100g') is None for name in ('energy-kcal', 'energy-kj')):
        nutrients.append(
            'energy-kcal' if nutriments.get('energy-kcal_serving') is not None else 'energy-kj'
        )

    missing = [
        nutrient
        for nutrient in nutrients
        if nutriments.get(f'{nutrient}_100g') is None
        and nutriments.get(f'{nutrient}_serving') is not None
    ]
    if not missing or (mass := _serving_weight_for_nutrients(product_data)) is None:
        return nutriments
    if mass < MIN_SERVING_MASS_GRAMS:
        return nutriments

    for nutrient in missing:
        value = nutriments[f'{nutrient}_serving']
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise ValueError(f'Invalid per-serving value for {nutrient}: {value!r}')
        try:
            numeric_value = float(value)
        except (ValueError, OverflowError) as error:
            raise ValueError(f'Invalid per-serving value for {nutrient}: {value!r}') from error
        if not math.isfinite(numeric_value) or value < 0:
            raise ValueError(f'Invalid per-serving value for {nutrient}: {value!r}')
        per_100g = numeric_value / mass * 100
        if not math.isfinite(per_100g):
            raise ValueError(f'Invalid per-serving value for {nutrient}: {value!r}')
        nutriments[f'{nutrient}_100g'] = per_100g

    return nutriments


def extract_serving_size_data(
    serving_size: str,
    language_code: str | None = None,
) -> tuple[int | None, str | None, float | None]:
    if not serving_size:
        return None, None, None

    # Parse textual amount/unit even if no explicit mass value is present.
    amount = 1.0
    with translation.override(language_code):
        unit = gettext('Serving')

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
        with translation.override(language_code):
            unit = gettext('Serving')

    mass = _serving_mass_in_grams(serving_size)
    return round(mass) if mass is not None else None, unit[:200], amount


def extract_info_from_off(product_data: dict, language: int) -> IngredientData:
    if not all(req in product_data for req in OFF_REQUIRED_TOP_LEVEL):
        raise KeyError('Missing required top-level key')

    nutriments = _nutriments_with_serving_fallback(product_data)
    if not all(nutriments.get(req) is not None for req in OFF_REQUIRED_NUTRIMENTS):
        raise KeyError('Missing required nutrition key')

    # Basics
    # Prefer the generic product_name, then the product's own language, then English,
    # then any other localized name
    lang = product_data.get('lang', '')
    name = (
        product_data.get('product_name')
        or product_data.get(f'product_name_{lang}')
        or product_data.get('product_name_en')
    )
    if not name:
        for key, value in product_data.items():
            if key.startswith('product_name_') and value:
                name = value
                break
    if not name:
        raise KeyError('Missing required product name')

    common_name = product_data.get('generic_name', '')

    # If the energy is not available in kcal, convert from kJ
    if nutriments.get('energy-kcal_100g') is not None:
        energy = nutriments['energy-kcal_100g']
    elif nutriments.get('energy-kj_100g') is not None:
        energy = nutriments['energy-kj_100g'] / KJ_PER_KCAL
    else:
        raise KeyError('Energy is not available')

    code = product_data['code']
    protein = nutriments['proteins_100g']
    carbs = nutriments['carbohydrates_100g']
    fat = nutriments['fat_100g']

    # these are optional
    saturated = nutriments.get('saturated-fat_100g', None)
    sodium = nutriments.get('sodium_100g', None)
    sugars = nutriments.get('sugars_100g', None)
    fiber = nutriments.get('fiber_100g', None)
    brand = product_data.get('brands', '')
    serving_size = product_data.get('serving_size', '')

    language_code = product_data.get('lang')
    serving_size_gram, serving_size_unit, serving_size_amount = extract_serving_size_data(
        serving_size, language_code
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
