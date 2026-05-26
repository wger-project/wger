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
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

# Third Party
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.headless_long_lived import LONG_LIVED_FLAG


class IssueRefreshTokenApiTestCase(WgerTestCase):
    """
    Tests the ``/api/v2/issue-refresh-token`` endpoint that lets clients holding
    a legacy DRF API token migrate to the headless JWT auth surface without
    re-prompting the user for credentials.
    """

    url = '/api/v2/issue-refresh-token'

    def test_drf_token_mints_a_usable_refresh_token(self):
        """
        Happy path: POST with ``Authorization: Token <key>`` returns a
        refresh token that the existing ``/tokens/refresh`` endpoint
        accepts and exchanges for a full access bundle. This is the exact
        round-trip the Flutter migration flow runs on first launch.
        """
        user = User.objects.get(username='test')
        legacy_token, _ = Token.objects.get_or_create(user=user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {legacy_token.key}')
        mint_response = client.post(self.url)

        self.assertEqual(mint_response.status_code, 200)
        refresh_token = mint_response.json().get('refresh_token')
        self.assertIsInstance(refresh_token, str)
        self.assertTrue(refresh_token)

        # The minted refresh token has to round-trip through the existing
        # exchange endpoint without us having to know its internal shape.
        anon = APIClient()
        exchange = anon.post(
            '/_allauth/app/v1/tokens/refresh',
            data={'refresh_token': refresh_token},
            format='json',
        )
        self.assertEqual(exchange.status_code, 200)
        body = exchange.json()
        self.assertIn('access_token', body['data'])

    def test_session_is_tagged_as_long_lived(self):
        """
        The minted refresh token is backed by a dedicated session row with
        the long-lived flag set, so the user can see and revoke it from
        the "API sessions" list on the api-key page later. Without this
        marker the row would look like a regular browser session.
        """
        user = User.objects.get(username='test')
        legacy_token, _ = Token.objects.get_or_create(user=user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {legacy_token.key}')
        response = client.post(self.url)
        self.assertEqual(response.status_code, 200)

        long_lived = [s for s in Session.objects.all() if s.get_decoded().get(LONG_LIVED_FLAG)]
        self.assertEqual(len(long_lived), 1)

    def test_unauthenticated_request_is_rejected(self):
        """
        No credentials means no refresh token. The endpoint must not leak
        information about whether a user exists; a 401/403 is enough.
        """
        response = APIClient().post(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_invalid_drf_token_is_rejected(self):
        """
        A garbage DRF token must not mint a refresh token. The
        ``IsAuthenticated`` permission catches this because the auth
        chain finds no matching ``Token`` row.
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token not-a-real-token-key')
        response = client.post(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_get_is_not_allowed(self):
        """
        Token minting is a state-changing action — a GET request must not
        be routed to the view. Matches the same defence the web
        ``api-key`` view has against attacker-embedded links / images that
        could otherwise rotate tokens silently.
        """
        user = User.objects.get(username='test')
        legacy_token, _ = Token.objects.get_or_create(user=user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {legacy_token.key}')
        response = client.get(self.url)

        self.assertEqual(response.status_code, 405)
        # No long-lived session must have been created for this user.
        long_lived = [s for s in Session.objects.all() if s.get_decoded().get(LONG_LIVED_FLAG)]
        self.assertEqual(long_lived, [])
