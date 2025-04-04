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
from unittest.mock import (
    Mock,
    patch,
)

# Django
from django.core.management import CommandError

# Third Party
from packaging.version import Version

# wger
from wger.core.api.min_server_version import check_min_server_version
from wger.version import VERSION


class TestCheckMinServerVersion(unittest.TestCase):
    @patch('wger.core.api.min_server_version.requests.get')
    def test_version_ok(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = str(VERSION)
        mock_get.return_value = mock_response

        try:
            check_min_server_version('https://example.com')
        except CommandError:
            self.fail('check_min_server_version raised CommandError unexpectedly!')

    @patch('wger.core.api.min_server_version.requests.get')
    def test_version_too_low(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = str(Version('999.0.0'))
        mock_get.return_value = mock_response

        with self.assertRaises(CommandError):
            check_min_server_version('https://example.com')
