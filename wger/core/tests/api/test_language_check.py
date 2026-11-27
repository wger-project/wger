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

# Standard Library
from unittest import mock

# Django
from django.core.cache import cache
from django.urls import reverse

# Third Party
from rest_framework import status
from rest_framework.settings import api_settings

# wger
from wger.core.api.serializers import LanguageCheckSerializer
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

    def test_detection_only_reads_the_start_of_long_inputs(self):
        """
        Language detection runs over at most MAX_DETECTION_LENGTH characters of the input
        """
        text = 'Hallo Welt - das ist ein Test. ' * 50_000
        with mock.patch('wger.core.api.serializers.LanguageDetectorBuilder') as builder:
            detector = builder.from_all_languages.return_value.build.return_value
            detector.detect_language_of.return_value.iso_code_639_1.name = 'DE'
            response = self.client.post(
                reverse('check-language'), data={'language_code': 'de', 'input': text}
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        analysed = detector.detect_language_of.call_args.args[0]
        self.assertEqual(analysed, text[: LanguageCheckSerializer.MAX_DETECTION_LENGTH])
        confidence_input = detector.compute_language_confidence_values.call_args.args[0]
        self.assertEqual(confidence_input, analysed)

    def test_anonymous_requests_are_throttled(self):
        """
        Requests above the language_check rate are answered with 429
        """
        cache.clear()
        self.addCleanup(cache.clear)
        data = {'language_code': 'de', 'input': 'Hallo Welt - das ist ein Test'}

        with mock.patch.dict(api_settings.DEFAULT_THROTTLE_RATES, {'language_check': '1/min'}):
            first = self.client.post(reverse('check-language'), data=data)
            second = self.client.post(reverse('check-language'), data=data)

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
