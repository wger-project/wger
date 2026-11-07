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

# Standard Library
import enum


class SyncMode(enum.Enum):
    """
    Mode for ingredient sync/import scripts.

    INSERT: bulk-insert new ingredients (very fast, use for empty databases)
    UPDATE: update existing ingredients or create new ones (slower, 2 queries per product)
    """

    INSERT = enum.auto()
    UPDATE = enum.auto()


ENERGY_FACTOR = {
    'protein': 4,
    'carbohydrates': 4,
    'fat': 9,
    'fiber': 2,
}
"""
Simple approximation of energy (kcal) provided per gram

The values are the conversion factors from EU Regulation 1169/2011, Annex XIV
"""

ENERGY_CHECK_MIN_KCAL = 13
ENERGY_CHECK_TOLERANCE_RELATIVE = 0.3
ENERGY_CHECK_TOLERANCE_ABSOLUTE_KCAL = 5
"""
Thresholds for comparing the declared energy of an ingredient with the energy
computed from its macronutrients. These match the ones Open Food Facts uses for
its "energy-value-in-kcal-does-not-match-value-computed-from-other-nutrients"
data quality check: values of up to 13 kcal are not checked at all (too many
false positives) and larger ones may deviate by 30% plus a flat 5 kcal, since
nutrients we do not track (polyols, organic acids, alcohol) also contribute to
the declared energy.
"""

KJ_PER_KCAL = 4.184

OFF_FULL_DUMP_URL = 'https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz'
