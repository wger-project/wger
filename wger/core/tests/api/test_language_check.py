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
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase


class LanguageCheckApiTestCase(BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/check-language/'

    def test_check_correct_language_with_code(self):
        """
        Test that the language is correctly detected - using language code
        """
        response = self.client.post(
            self.url, data={'language_code': 'de', 'input': 'Hallo Welt - das ist ein Test'}
        ).json()
        self.assertEqual(response, {'result': True})
        self.assertFalse(response.get('check'))

    def test_check_correct_language_with_id(self):
        """
        Test that the language is correctly detected - using language id
        """
        response = self.client.post(
            self.url, data={'language': 1, 'input': 'Hallo Welt - das ist ein Test'}
        ).json()
        self.assertEqual(response, {'result': True})
        self.assertFalse(response.get('check'))

    def test_check_wrong_language(self):
        """
        Test that the wrong language results in an error
        """
        response = self.client.post(
            self.url, data={'language_code': 'fr', 'input': 'a breed of hunting dog from Japan.'}
        ).json()
        self.assertTrue(response['check'].get('detected_language'))

    def test_unknown_language(self):
        """
        Test that an unknown language returns an error
        """
        response = self.client.post(
            self.url, data={'language_code': 'zz', 'input': 'a breed of hunting dog from Japan.'}
        ).json()
        self.assertTrue(response.get('language'))

    def test_no_languages(self):
        """
        Test that either a language ID or a language code must be provided
        """
        response = self.client.post(
            self.url, data={'input': 'a breed of hunting dog from Japan.'}
        ).json()
        self.assertTrue(response.get('language'))
