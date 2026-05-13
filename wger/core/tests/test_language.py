# -*- coding: utf-8 -*-

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
from django.urls import (
    reverse,
    reverse_lazy,
)

# wger
from wger.core.models import Language
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    WgerAccessTestCase,
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
)


class LanguageRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(f'{Language.objects.get(pk=1)}', 'Deutsch (de)')


class LanguageOverviewTest(WgerAccessTestCase):
    """
    Tests accessing the system's languages
    """

    url = 'core:language:overview'
    anonymous_fail = True


class LanguageDetailViewTest(WgerAccessTestCase):
    """
    Tests accessing a detail view of a language
    """

    url = reverse_lazy('core:language:view', kwargs={'pk': 1})
    anonymous_fail = True


class CreateLanguageTestCase(WgerAddTestCase):
    """
    Tests adding a new language
    """

    object_class = Language
    url = 'core:language:add'
    data = {'short_name': 'dk', 'full_name': 'Dansk', 'full_name_en': 'Danish'}


class EditLanguageTestCase(WgerEditTestCase):
    """
    Tests adding a new language
    """

    object_class = Language
    url = 'core:language:edit'
    pk = 1
    data = {'short_name': 'dk', 'full_name': 'Dansk', 'full_name_en': 'Danish'}


class DeleteLanguageTestCase(WgerDeleteTestCase):
    """
    Tests adding a new language
    """

    object_class = Language
    url = 'core:language:delete'
    pk = 1


class UseBrowserLanguageRedirectTestCase(WgerTestCase):
    """
    The ``?next=`` parameter must only redirect to the same origin.
    """

    URL = reverse_lazy('core:language:browser_language')

    def test_open_redirect_protocol_relative_blocked(self):
        response = self.client.get(self.URL, {'next': '//evil.example/x'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            response['Location'].startswith('//evil.example'),
            msg=f'open redirect to {response["Location"]!r}',
        )

    def test_open_redirect_absolute_url_blocked(self):
        response = self.client.get(self.URL, {'next': 'https://evil.example/'})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil.example', response['Location'])

    def test_open_redirect_url_encoded_blocked(self):
        response = self.client.get(self.URL + '?next=%2F%2Fevil.example%2Fx')
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil.example', response['Location'])

    def test_safe_relative_next_passes_through(self):
        response = self.client.get(self.URL, {'next': '/exercise/overview'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/exercise/overview')

    def test_language_prefix_is_still_stripped(self):
        response = self.client.get(self.URL, {'next': '/en/exercise/overview'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/exercise/overview')


class LanguageApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the language overview resource
    """

    pk = 1
    resource = Language
    private_resource = False
    overview_cached = True
