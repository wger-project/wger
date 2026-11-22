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
from unittest.mock import (
    Mock,
    call,
    patch,
)

# Django
from django.test import (
    SimpleTestCase,
    override_settings,
)

# wger
from wger.utils.requests import (
    WgerTimeoutSession,
    get_all_paginated,
    get_paginated,
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


@override_settings(WGER_REQUEST_TIMEOUT=123)
class PaginatedRequestsTestCase(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.url = 'https://example.com/results/'
        self.next_url = 'https://example.com/results/?page=2'
        self.final_url = 'https://example.com/results/?page=3'
        self.headers = {'X-Test-Header': 'pagination'}

    def test_multiple_pages(self):
        """Both helpers preserve result order and request options through the final page."""
        pages = [
            {'results': [3, 1], 'next': self.next_url},
            {'results': [4, 1], 'next': self.final_url},
            {'results': [5], 'next': None},
        ]

        for helper in (get_all_paginated, get_paginated):
            with (
                self.subTest(helper=helper.__name__),
                patch('wger.utils.requests.requests.get') as mock_get,
            ):
                mock_get.side_effect = [Mock(json=Mock(return_value=page)) for page in pages]

                self.assertEqual(list(helper(self.url, headers=self.headers)), [3, 1, 4, 1, 5])
                self.assertEqual(
                    mock_get.call_args_list,
                    [
                        call(self.url, headers=self.headers, timeout=(10, 123)),
                        call(self.next_url, headers=self.headers, timeout=(10, 123)),
                        call(self.final_url, headers=self.headers, timeout=(10, 123)),
                    ],
                )

    def test_empty_final_page(self):
        """Both helpers keep earlier results and stop after an empty final page."""
        pages = [
            {'results': [1, 2], 'next': self.next_url},
            {'results': [], 'next': None},
        ]

        for helper in (get_all_paginated, get_paginated):
            with (
                self.subTest(helper=helper.__name__),
                patch('wger.utils.requests.requests.get') as mock_get,
            ):
                mock_get.side_effect = [Mock(json=Mock(return_value=page)) for page in pages]

                self.assertEqual(list(helper(self.url, headers=self.headers)), [1, 2])
                self.assertEqual(
                    mock_get.call_args_list,
                    [
                        call(self.url, headers=self.headers, timeout=(10, 123)),
                        call(self.next_url, headers=self.headers, timeout=(10, 123)),
                    ],
                )

    def test_empty_intermediate_page(self):
        """Both helpers follow the next link even when an intermediate page is empty."""
        pages = [
            {'results': [1, 2], 'next': self.next_url},
            {'results': [], 'next': self.final_url},
            {'results': [3, 4], 'next': None},
        ]

        for helper in (get_all_paginated, get_paginated):
            with (
                self.subTest(helper=helper.__name__),
                patch('wger.utils.requests.requests.get') as mock_get,
            ):
                mock_get.side_effect = [Mock(json=Mock(return_value=page)) for page in pages]

                self.assertEqual(list(helper(self.url, headers=self.headers)), [1, 2, 3, 4])
                self.assertEqual(
                    mock_get.call_args_list,
                    [
                        call(self.url, headers=self.headers, timeout=(10, 123)),
                        call(self.next_url, headers=self.headers, timeout=(10, 123)),
                        call(self.final_url, headers=self.headers, timeout=(10, 123)),
                    ],
                )

    @patch('wger.utils.requests.requests.get')
    def test_get_paginated_fetches_lazily(self, mock_get):
        """The generator requests a page only when iteration needs a result from it."""
        pages = [
            {'results': [1, 2], 'next': self.next_url},
            {'results': [3, 4], 'next': None},
        ]
        mock_get.side_effect = [Mock(json=Mock(return_value=page)) for page in pages]

        results = get_paginated(self.url, headers=self.headers)
        mock_get.assert_not_called()

        self.assertEqual(next(results), 1)
        mock_get.assert_called_once_with(self.url, headers=self.headers, timeout=(10, 123))

        self.assertEqual(next(results), 2)
        mock_get.assert_called_once_with(self.url, headers=self.headers, timeout=(10, 123))

        self.assertEqual(next(results), 3)
        self.assertEqual(mock_get.call_count, 2)

        self.assertEqual(next(results), 4)
        self.assertEqual(mock_get.call_count, 2)

        with self.assertRaises(StopIteration):
            next(results)

        self.assertEqual(
            mock_get.call_args_list,
            [
                call(self.url, headers=self.headers, timeout=(10, 123)),
                call(self.next_url, headers=self.headers, timeout=(10, 123)),
            ],
        )
