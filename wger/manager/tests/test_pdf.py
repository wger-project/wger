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
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase


class RoutinePdfLogExportTestCase(WgerTestCase):
    """
    Tests exporting a routine as a PDF - logs
    """

    def export_pdf(self, fail=False):
        """
        Helper function to test exporting a routine as a pdf
        """
        response = self.client.get(reverse('manager:routine:pdf-log', kwargs={'pk': 3}))

        if fail:
            self.assertIn(response.status_code, (403, 404, 302))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')

            # Approximate size only
            self.assertGreater(int(response['Content-Length']), 38000)
            self.assertLess(int(response['Content-Length']), 42000)

    def export_pdf_with_comments(self, fail=False):
        """
        Helper function to test exporting a workout as a pdf, with exercise coments
        """

        response = self.client.get(
            reverse('manager:routine:pdf-log', kwargs={'id': 3, 'comments': 0})
        )

        if fail:
            self.assertIn(response.status_code, (403, 404, 302))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')

            # Approximate size only
            self.assertGreater(int(response['Content-Length']), 38000)
            self.assertLess(int(response['Content-Length']), 42000)

    def test_export_pdf_anonymous(self):
        """
        Tests exporting a workout as a pdf as an anonymous user
        """

        self.export_pdf(fail=True)

    def test_export_pdf_owner(self):
        """
        Tests exporting a workout as a pdf as the owner user
        """

        self.user_login('test')
        self.export_pdf(fail=False)

    def test_export_pdf_other(self):
        """
        Tests exporting a workout as a pdf as a logged user not owning the data
        """

        self.user_login('admin')
        self.export_pdf(fail=True)


class RoutinePdfTableExportTestCase(WgerTestCase):
    """
    Tests exporting a routine as a PDF - table
    """

    def export_pdf(self, fail=False):
        """
        Helper function to test exporting a routine as a pdf
        """

        response = self.client.get(reverse('manager:routine:pdf-table', kwargs={'pk': 3}))

        if fail:
            self.assertIn(response.status_code, (403, 404, 302))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')

            # Approximate size only
            self.assertGreater(int(response['Content-Length']), 38000)
            self.assertLess(int(response['Content-Length']), 42000)

    def test_export_pdf_anonymous(self):
        """
        Tests exporting a workout as a pdf as an anonymous user
        """

        self.export_pdf(fail=True)

    def test_export_pdf_owner(self):
        """
        Tests exporting a workout as a pdf as the owner user
        """

        self.user_login('test')
        self.export_pdf(fail=False)

    def test_export_pdf_other(self):
        """
        Tests exporting a workout as a pdf as a logged user not owning the data
        """

        self.user_login('admin')
        self.export_pdf(fail=True)
