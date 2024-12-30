#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
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

MEALITEM_WEIGHT_GRAM = '1'
MEALITEM_WEIGHT_UNIT = '2'

ENERGY_FACTOR = {
    'protein': {'kg': 4, 'lb': 113},
    'carbohydrates': {'kg': 4, 'lb': 113},
    'fat': {'kg': 9, 'lb': 225},
}
"""
Simple approximation of energy (kcal) provided per gram or ounce
"""

KJ_PER_KCAL = 4.184
