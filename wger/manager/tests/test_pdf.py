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

# Django
from django.urls import reverse

# Third Party
from reportlab.platypus import Paragraph

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import Routine


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


class RoutinePdfEscapingTestCase(WgerTestCase):
    """
    Tests that user submitted text is escaped before it is passed to reportlab
    """

    name = 'Squat <img src=x.png>'
    description = 'Bench <img src="http://localhost:1/x.png"/>'

    def setUp(self):
        super().setUp()

        routine = Routine.objects.get(pk=3)
        routine.name = self.name
        routine.description = self.description
        routine.save()

        self.user_login('test')

    def paragraph_markup(self, url_name):
        """
        Returns the markup of every Paragraph the view builds itself
        """
        with patch('wger.manager.views.pdf.Paragraph', side_effect=Paragraph) as paragraph:
            response = self.client.get(reverse(url_name, kwargs={'pk': 3}))

        self.assertEqual(response.status_code, 200)
        return [call.args[0] for call in paragraph.call_args_list]

    def test_log_pdf_escapes_routine_text(self):
        markup = self.paragraph_markup('manager:routine:pdf-log')

        self.assertTrue(markup)
        for entry in markup:
            self.assertNotIn('<img', entry)
        self.assertIn('&lt;img', ' '.join(markup))

    def test_table_pdf_escapes_routine_text(self):
        markup = self.paragraph_markup('manager:routine:pdf-table')

        self.assertTrue(markup)
        for entry in markup:
            self.assertNotIn('<img', entry)
        self.assertIn('&lt;img', ' '.join(markup))
