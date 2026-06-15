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
from urllib.parse import (
    parse_qs,
    urlparse,
)

# Django
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase


class AppAuthHandoffTestCase(WgerTestCase):
    """
    Tests for the /user/app-auth/ web-handoff view that mints a long-lived
    refresh token and redirects to a custom URL scheme.
    """

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('core:user:app-auth-handoff'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])

    def test_authenticated_user_gets_redirect_page(self):
        self.user_login('test')
        response = self.client.get(reverse('core:user:app-auth-handoff'))
        self.assertEqual(response.status_code, 200)
        # Meta-refresh carries the custom-scheme URL.
        self.assertContains(response, 'http-equiv="refresh"')
        self.assertContains(response, 'wger://app-auth#token=')

    def test_state_is_echoed_back_in_fragment(self):
        self.user_login('test')
        response = self.client.get(
            reverse('core:user:app-auth-handoff') + '?state=abc123_-XYZ',
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'state=abc123_-XYZ')
        self.assertContains(response, 'token=')

    def test_state_with_disallowed_characters_is_dropped(self):
        self.user_login('test')
        response = self.client.get(
            reverse('core:user:app-auth-handoff') + '?state=abc%20def',
        )
        self.assertEqual(response.status_code, 200)
        # No reflected state in the redirect URL, but the token is still issued.
        self.assertContains(response, 'token=')
        self.assertNotContains(response, 'state=')

    def test_oversized_state_is_dropped(self):
        self.user_login('test')
        long_state = 'a' * 200
        response = self.client.get(
            reverse('core:user:app-auth-handoff') + f'?state={long_state}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'state=')

    def test_token_is_in_fragment_not_query(self):
        self.user_login('test')
        response = self.client.get(reverse('core:user:app-auth-handoff'))
        content = response.content.decode()
        # Extract the return_uri from the meta-refresh content attribute.
        start = content.index('0;url=') + len('0;url=')
        end = content.index('"', start)
        return_uri = content[start:end]
        parsed = urlparse(return_uri)
        self.assertEqual(parsed.scheme, 'wger')
        # Fragment carries the token; query is empty.
        self.assertEqual(parsed.query, '')
        self.assertTrue(parsed.fragment.startswith('token='))
        self.assertGreater(len(parsed.fragment), len('token='))
