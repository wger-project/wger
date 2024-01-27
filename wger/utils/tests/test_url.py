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

# wger
from wger.utils.url import make_uri


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
            make_uri('test', id=123),
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
            make_uri('test', id=123, object_method='create', query={'key1': 'value1'}),
            'https://wger.de/api/v2/test/123/create/?key1=value1',
        )


if __name__ == '__main__':
    unittest.main()
