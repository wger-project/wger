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
from wger.utils.constants import ODBL_LICENSE_ID


def extract_info_from_wger_api(product_data: dict) -> IngredientData:
    # Basics
    name = product_data.get('name')
    common_name = product_data.get('common_name', '')
    code = product_data['code']
    energy = float(product_data['energy'])
    protein = float(product_data['protein'])
    carbs = float(product_data['carbohydrates'])
    fat = float(product_data['fat'])
    language = product_data['language']

    # Optional
    sodium = product_data.get('sodium', None)
    sodium = float(sodium) if sodium is not None else None

    saturated_fat = product_data.get('fat_saturated', None)
    saturated_fat = float(saturated_fat) if saturated_fat is not None else None

    sugars = product_data.get('carbohydrates_sugar', None)
    sugars = float(sugars) if sugars is not None else None

    fiber = product_data.get('fiber', None)
    fiber = float(fiber) if fiber is not None else None

    brand = product_data.get('brand', '')

    # License and author info
    source_name = product_data.get('source_name', '')
    source_url = product_data.get('source_url', '')

    license_id = product_data.get('license', ODBL_LICENSE_ID)
    license_title = product_data.get('license_title', '')
    license_object_url = product_data.get('license_object_url', '')
    license_authors = product_data.get('authors', '')
    license_author_url = product_data.get('license_author_url', '')
    license_derivative_source_url = product_data.get('license_derivative_source_url', '')

    ingredient_data = IngredientData(
        remote_id=code,
        name=name,
        language_id=language,
        energy=energy,
        protein=protein,
        carbohydrates=carbs,
        carbohydrates_sugar=sugars,
        fat=fat,
        fat_saturated=saturated_fat,
        fiber=fiber,
        sodium=sodium,
        code=code,
        source_name=source_name,
        source_url=source_url,
        common_name=common_name,
        brand=brand,
        license_id=license_id,
        license_title=license_title,
        license_object_url=license_object_url,
        license_author=license_authors,
        license_author_url=license_author_url,
        license_derivative_source_url=license_derivative_source_url,
    )
    return ingredient_data
