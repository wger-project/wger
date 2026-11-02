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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Django
from django.test import SimpleTestCase

# wger
from wger.nutrition.models import Ingredient


class DeriveServingSizeGramTestCase(SimpleTestCase):
    """
    Test deriving the gram weight of a serving from its amount and unit
    """

    def test_valid_amount(self):
        self.assertEqual(Ingredient._derive_serving_size_gram(1.5, 'l'), 1500)

    def test_negative_amount(self):
        self.assertIsNone(Ingredient._derive_serving_size_gram(-1, 'l'))

    def test_infinite_amount(self):
        self.assertIsNone(Ingredient._derive_serving_size_gram(float('inf'), 'l'))
