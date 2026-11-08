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
from django.test import (
    SimpleTestCase,
    override_settings,
)

# wger
from wger.utils.requests import (
    WgerTimeoutSession,
    wger_request_timeout,
)


class WgerRequestTimeoutTestCase(SimpleTestCase):
    @override_settings(WGER_REQUEST_TIMEOUT=123)
    def test_read_timeout_from_settings(self):
        """The read timeout comes from WGER_REQUEST_TIMEOUT, the connect timeout is fixed"""
        self.assertEqual(wger_request_timeout(), (10, 123))


class WgerTimeoutSessionTestCase(SimpleTestCase):
    @override_settings(WGER_REQUEST_TIMEOUT=123)
    @patch('requests.Session.request')
    def test_default_timeout(self, mock_request):
        """Requests without a timeout get wger_request_timeout()"""
        WgerTimeoutSession().get('https://example.com')

        self.assertEqual(mock_request.call_args.kwargs['timeout'], (10, 123))

    @patch('requests.Session.request')
    def test_explicit_timeout_is_kept(self, mock_request):
        """A timeout passed by the caller is not overwritten"""
        WgerTimeoutSession().get('https://example.com', timeout=3)

        self.assertEqual(mock_request.call_args.kwargs['timeout'], 3)
