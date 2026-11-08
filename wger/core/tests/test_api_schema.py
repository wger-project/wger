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
from django.conf import settings
from django.test import override_settings
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase


class ApiSchemaTestCase(WgerTestCase):
    """
    Test the API schema and documentation endpoints
    """

    def test_schema(self):
        """The schema endpoint generates the schema"""

        response = self.client.get(reverse('schema'))
        self.assertEqual(response.status_code, 200)

    def test_schema_without_site_url(self):
        """The schema is generated even when SITE_URL is not configured"""

        with override_settings():
            del settings.SITE_URL
            response = self.client.get(reverse('schema'))

        self.assertEqual(response.status_code, 200)

    def test_swagger_ui(self):
        """The swagger UI page renders"""

        response = self.client.get(reverse('api-swagger-ui'))
        self.assertEqual(response.status_code, 200)

    def test_redoc(self):
        """The redoc page renders"""

        response = self.client.get(reverse('api-redoc'))
        self.assertEqual(response.status_code, 200)

    def test_swagger_ui_options(self):
        """An OPTIONS request to the swagger UI does not crash the template rendering"""

        response = self.client.options(reverse('api-swagger-ui'))
        self.assertEqual(response.status_code, 405)

    def test_redoc_options(self):
        """An OPTIONS request to the redoc page does not crash the template rendering"""

        response = self.client.options(reverse('api-redoc'))
        self.assertEqual(response.status_code, 405)
