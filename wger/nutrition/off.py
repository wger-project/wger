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
from wger.core.models import Language
from wger.nutrition.models import Source
from wger.utils.constants import CC_ODBL_LICENSE_ID
from wger.utils.models import AbstractSubmissionModel


OFF_REQUIRED_TOP_LEVEL = [
    'product_name',
    'code',
    'nutriments',
]
OFF_REQUIRED_NUTRIMENTS = [
    'energy-kcal_100g',
    'proteins_100g',
    'carbohydrates_100g',
    'sugars_100g',
    'fat_100g',
    'saturated-fat_100g',
]


def extract_info_from_off(product, language):

    if not all(req in product for req in OFF_REQUIRED_TOP_LEVEL):
        raise KeyError('Missing required top-level key')

    if not all(req in product['nutriments'] for req in OFF_REQUIRED_NUTRIMENTS):
        raise KeyError('Missing required nutrition key')

    # Basics
    name = product['product_name']
    if name is None:
        raise KeyError('Product name is None')
    if len(name) > 200:
        name = name[:200]

    common_name = product.get('generic_name', '')
    common_name = '' if common_name is None else common_name
    if len(common_name) > 200:
        common_name = common_name[:200]

    code = product['code']
    energy = product['nutriments']['energy-kcal_100g']
    protein = product['nutriments']['proteins_100g']
    carbs = product['nutriments']['carbohydrates_100g']
    sugars = product['nutriments']['sugars_100g']
    fat = product['nutriments']['fat_100g']
    saturated = product['nutriments']['saturated-fat_100g']

    # these are optional
    sodium = product['nutriments'].get('sodium_100g', None)
    fibre = product['nutriments'].get('fiber_100g', None)
    brand = product.get('brands', None)

    # License and author info
    source_name = Source.OPEN_FOOD_FACTS.value
    source_url = f'https://world.openfoodfacts.org/api/v2/product/{code}.json'
    authors = ', '.join(product.get('editors_tags', ['open food facts']))

    return {
        'name': name,
        'language': language,
        'energy': energy,
        'protein': protein,
        'carbohydrates': carbs,
        'carbohydrates_sugar': sugars,
        'fat': fat,
        'fat_saturated': saturated,
        'fibres': fibre,
        'sodium': sodium,
        'code': code,
        'source_name': source_name,
        'source_url': source_url,
        'common_name': common_name,
        'brand': brand,
        'status': AbstractSubmissionModel.STATUS_ACCEPTED,
        'license_id': CC_ODBL_LICENSE_ID,
        'license_author': authors,
        'license_title': name,
        'license_object_url': f'https://world.openfoodfacts.org/product/{code}/'
    }
