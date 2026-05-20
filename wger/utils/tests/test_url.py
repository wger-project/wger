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
import unittest

# Django
from django.test import (
    RequestFactory,
    override_settings,
)

# wger
from wger.utils.url import (
    make_absolute_url,
    make_uri,
)


class TestMakeUri(unittest.TestCase):
    def test_make_uri(self):
        # Test default server_url
        self.assertEqual(
            make_uri('test'),
            'https://wger.de/api/v2/test/',
        )

        # Test custom server_url
        self.assertEqual(
            make_uri('test', server_url='https://api.example.com'),
            'https://api.example.com/api/v2/test/',
        )

        # Test with id
        self.assertEqual(
            make_uri('test', object_id=123),
            'https://wger.de/api/v2/test/123/',
        )

        # Test with object_method
        self.assertEqual(
            make_uri('test', object_method='create'),
            'https://wger.de/api/v2/test/create/',
        )

        # Test with query parameters
        self.assertEqual(
            make_uri('endpoint', query={'key1': 'value1', 'key2': 'value2'}),
            'https://wger.de/api/v2/endpoint/?key1=value1&key2=value2',
        )

        # Test with all parameters
        self.assertEqual(
            make_uri('test', object_id=123, object_method='create', query={'key1': 'value1'}),
            'https://wger.de/api/v2/test/123/create/?key1=value1',
        )


class TestMakeAbsoluteUrl(unittest.TestCase):
    def test_with_request_uses_request_host(self):
        request = RequestFactory().get('/')
        self.assertEqual(
            make_absolute_url('/media/exercise-images/foo.png', request),
            'http://testserver/media/exercise-images/foo.png',
        )

    def test_without_request_falls_back_to_site_url(self):
        with override_settings(SITE_URL='https://example.com'):
            self.assertEqual(
                make_absolute_url('/media/exercise-images/foo.png'),
                'https://example.com/media/exercise-images/foo.png',
            )

    def test_empty_path_is_returned_unchanged(self):
        self.assertIsNone(make_absolute_url(None))
        self.assertEqual(make_absolute_url(''), '')


if __name__ == '__main__':
    unittest.main()
