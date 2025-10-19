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

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# wger
from wger.core.models import Language
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.models import NutritionPlan


class NutritionalPlanPdfExportTestCase(WgerTestCase):
    """
    Tests exporting a nutritional plan as a pdf
    """

    def export_pdf(self, fail=False):
        """
        Helper function to test exporting a nutritional plan as a pdf
        """

        # Get a plan
        response = self.client.get(reverse('nutrition:plan:export-pdf', kwargs={'id': 4}))

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
