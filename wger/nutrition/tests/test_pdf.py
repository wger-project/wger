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

# Standard Library
from unittest.mock import patch
from xml.sax.saxutils import escape

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# Third Party
from reportlab.platypus import Paragraph

# wger
from wger.core.models import Language
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.models import (
    Ingredient,
    IngredientWeightUnit,
    MealItem,
    NutritionPlan,
)


class NutritionalPlanPdfExportTestCase(WgerTestCase):
    """
    Tests exporting a nutritional plan as a pdf
    """

    def export_pdf(self, fail=False):
        """
        Helper function to test exporting a nutritional plan as a pdf
        """

        # Get a plan
        response = self.client.get(
            reverse(
                'nutrition:plan:export-pdf',
                kwargs={'id': '11111111-1111-1111-1111-000000000004'},
            ),
        )

        if fail:
            self.assertIn(response.status_code, (404, 403))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertEqual(
                response['Content-Disposition'], 'attachment; filename=nutritional-plan.pdf'
            )

            # Approximate size
            self.assertGreater(int(response['Content-Length']), 38000)
            self.assertLess(int(response['Content-Length']), 42000)

        # Create an empty plan
        user = User.objects.get(pk=2)
        language = Language.objects.get(pk=1)
        plan = NutritionPlan()
        plan.user = user
        plan.language = language
        plan.save()
        response = self.client.get(reverse('nutrition:plan:export-pdf', kwargs={'id': plan.id}))

        if fail:
            self.assertIn(response.status_code, (404, 403))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertEqual(
                response['Content-Disposition'], 'attachment; filename=nutritional-plan.pdf'
            )

            # Approximate size
            self.assertGreater(int(response['Content-Length']), 38000)
            self.assertLess(int(response['Content-Length']), 42000)

    def test_export_pdf_anonymous(self):
        """
        Tests exporting a nutritional plan as a pdf as an anonymous user
        """

        self.export_pdf(fail=True)

    def test_export_pdf_owner(self):
        """
        Tests exporting a nutritional plan as a pdf as the owner user
        """

        self.user_login('test')
        self.export_pdf(fail=False)

    def test_export_pdf_other(self):
        """
        Tests exporting a nutritional plan as a pdf as a logged user not owning the data
        """

        self.user_login('admin')
        self.export_pdf(fail=True)


class NutritionalPlanPdfEscapingTestCase(WgerTestCase):
    """
    Tests that user submitted text is escaped before it is passed to reportlab
    """

    plan_id = '11111111-1111-1111-1111-000000000004'
    description = 'Cutting <img src=x.png>'
    ingredient_name = 'Beans <img src="http://localhost:1/x.png"/>'
    unit_name = 'Cup <img src=x.png>'

    def setUp(self):
        super().setUp()

        plan = NutritionPlan.objects.get(pk=self.plan_id)
        plan.description = self.description
        plan.save()

        Ingredient.objects.update(name=self.ingredient_name)
        for item in MealItem.objects.filter(meal__plan=plan):
            item.weight_unit = IngredientWeightUnit.objects.create(
                ingredient=item.ingredient,
                name=self.unit_name,
                gram=50,
            )
            item.save()

        self.user_login('test')

    def test_export_pdf_escapes_user_text(self):
        with patch('wger.nutrition.views.plan.Paragraph', side_effect=Paragraph) as paragraph:
            response = self.client.get(
                reverse('nutrition:plan:export-pdf', kwargs={'id': self.plan_id})
            )

        self.assertEqual(response.status_code, 200)
        markup = [call.args[0] for call in paragraph.call_args_list]

        self.assertTrue(markup)
        for entry in markup:
            self.assertNotIn('<img', entry)

        joined = ' '.join(markup)
        self.assertIn(escape(self.description), joined)
        self.assertIn(escape(self.ingredient_name), joined)
        self.assertIn(escape(self.unit_name), joined)
