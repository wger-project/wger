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

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.forms import MealItemForm
from wger.nutrition.models import (
    IngredientWeightUnit,
    MealItem,
)


class MealItemApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the meal overview resource
    """

    pk = 10
    resource = MealItem
    private_resource = True
    data = {
        'meal': 2,
        'amount': 100,
        'ingredient': 1,
    }


class MealItemFormTestCase(WgerTestCase):
    """
    Tests for meal item form quantity/unit behavior.
    """

    def test_weight_unit_field_has_explicit_grams_label(self):
        """
        The empty choice should clearly represent grams.
        """
        form = MealItemForm()
        self.assertEqual(str(form.fields['weight_unit'].empty_label), 'grams (g)')

    def test_weight_unit_choices_include_serving_label(self):
        """
        Serving-size options should include amount and gram conversion.
        """
        form = MealItemForm(data={'ingredient': 1})
        labels = [str(label) for _, label in form.fields['weight_unit'].choices]

        self.assertTrue(any(' = ' in label and label.endswith('g') for label in labels))
        self.assertTrue(
            all(
                unit.ingredient_id == 1
                for unit in form.fields['weight_unit'].queryset.select_related('ingredient')
            )
        )

    def test_weight_unit_queryset_accepts_ingredient_id_key(self):
        """
        The form should also support ingredient_id in bound data.
        """
        form = MealItemForm(data={'ingredient_id': 1})

        self.assertTrue(form.fields['weight_unit'].queryset.exists())
        self.assertTrue(
            all(
                unit.ingredient_id == 1
                for unit in form.fields['weight_unit'].queryset.select_related('ingredient')
            )
        )

    def test_invalid_ingredient_keeps_empty_weight_unit_queryset(self):
        """
        Invalid ingredient values should not crash and should keep unit choices empty.
        """
        form = MealItemForm(data={'ingredient': 'not-a-number'})

        self.assertEqual(form.fields['weight_unit'].queryset.count(), 0)
