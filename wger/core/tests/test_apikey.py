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
import importlib
import json
import logging
from datetime import timedelta
from unittest import mock

# Django
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

# Third Party
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

# wger
from wger.core.models import LongLivedSession
from wger.core.tasks import flush_expired_long_lived_sessions_task
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.headless_long_lived import (
    LONG_LIVED_CREATED_AT,
    LONG_LIVED_FLAG,
    list_long_lived_sessions,
    mint_long_lived_refresh_token,
)


logger = logging.getLogger(__name__)


class ApiKeyTestCase(WgerTestCase):
    """
    Tests the API key page
    """

    def test_api_key_page(self):
        """
        Tests the API key generation page
        """

        self.user_login('test')
        user = User.objects.get(username='test')

        # User already has a key
        response = self.client.get(reverse('core:user:api-key'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete current API key and generate new one')
        self.assertTrue(Token.objects.get(user=user))

        # User has no keys
        Token.objects.get(user=user).delete()
        response = self.client.get(reverse('core:user:api-key'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have no API key yet')
        self.assertRaises(Token.DoesNotExist, Token.objects.get, user=user)

    def test_api_key_page_generation(self):
        """
        User generates a new key
        """

        self.user_login('test')
        user = User.objects.get(username='test')
        key_before = Token.objects.get(user=user)

        response = self.client.post(reverse('core:user:api-key'), {'new_key': True})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response['Location'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete current API key and generate new one')

        key_after = Token.objects.get(user=user)
        self.assertTrue(key_after)

        # New key is different from the one before
        self.assertNotEqual(key_before.key, key_after.key)

    def test_api_key_can_be_deleted_without_replacement(self):
        """
        The "Delete API key" button removes the token without immediately
        creating a new one. Distinct from rotation, which is the existing
        ``new_key`` flow.
        """
        self.user_login('test')
        user = User.objects.get(username='test')
        self.assertTrue(Token.objects.filter(user=user).exists())

        response = self.client.post(reverse('core:user:api-key'), {'delete_key': 'true'})
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Token.objects.filter(user=user).exists())

    def test_api_key_delete_requires_post(self):
        """
        Same CSRF-via-img-tag concern as rotation: a GET must not destroy
        the user's token.
        """
        self.user_login('test')
        user = User.objects.get(username='test')
        key_before = Token.objects.get(user=user).key

        response = self.client.get(reverse('core:user:api-key'), {'delete_key': 'true'})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.get(user=user).key, key_before)

    def test_api_key_rotation_requires_post(self):
        """
        Token rotation is a state-changing action and must not be triggered
        by a GET request — otherwise an attacker could embed a link or
        image that silently rotates a victim's token.
        """
        self.user_login('test')
        user = User.objects.get(username='test')
        key_before = Token.objects.get(user=user)

        response = self.client.get(reverse('core:user:api-key'), {'new_key': True})
        self.assertEqual(response.status_code, 200)

        key_after = Token.objects.get(user=user)
        self.assertEqual(key_before.key, key_after.key)

    def test_revoke_jwt_sessions_blacklists_outstanding_refresh_tokens(self):
        """
        The "Revoke all API sessions" button on /user/api-key has to
        blacklist every still-usable refresh token for the current user,
        and a previously-issued refresh must stop minting access tokens.
        """
        api = APIClient()
        user = User.objects.get(username='test')
        old_refresh = str(RefreshToken.for_user(user))

        # Sanity baseline before the revoke
        refresh_before = api.post(
            '/api/v2/token/refresh',
            {'refresh': old_refresh},
            format='json',
        )
        self.assertEqual(refresh_before.status_code, 200)

        self.user_login('test')
        response = self.client.post(
            reverse('core:user:api-key'),
            {'revoke_jwt_sessions': 'true'},
        )
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username='test')
        outstanding = OutstandingToken.objects.filter(user=user)
        self.assertTrue(outstanding.exists())
        for ot in outstanding:
            self.assertTrue(BlacklistedToken.objects.filter(token=ot).exists())

        refresh_after = api.post(
            '/api/v2/token/refresh',
            {'refresh': old_refresh},
            format='json',
        )
        self.assertEqual(refresh_after.status_code, 401)

    def test_revoke_jwt_sessions_only_touches_current_user(self):
        """
        Hitting the revoke button as user 'test' must not blacklist the
        refresh tokens of an unrelated user (e.g. 'admin'). Cross-user
        leakage here would be a one-call DoS.
        """
        api_admin = APIClient()
        admin = User.objects.get(username='admin')
        admin_refresh = str(RefreshToken.for_user(admin))

        self.user_login('test')
        response = self.client.post(
            reverse('core:user:api-key'),
            {'revoke_jwt_sessions': 'true'},
        )
        self.assertEqual(response.status_code, 302)

        # The admin's refresh token is untouched
        admin_refresh_after = api_admin.post(
            '/api/v2/token/refresh',
            {'refresh': admin_refresh},
            format='json',
        )
        self.assertEqual(admin_refresh_after.status_code, 200)

    def test_revoke_jwt_sessions_requires_post(self):
        """
        Same CSRF concern as ``new_key``: a GET must not blacklist anything,
        otherwise an attacker could embed an <img src=...> that silently
        kills the victim's mobile sessions.
        """
        api = APIClient()
        user = User.objects.get(username='test')
        old_refresh = str(RefreshToken.for_user(user))

        self.user_login('test')
        response = self.client.get(
            reverse('core:user:api-key'),
            {'revoke_jwt_sessions': 'true'},
        )
        self.assertEqual(response.status_code, 200)

        refresh_after = api.post(
            '/api/v2/token/refresh',
            {'refresh': old_refresh},
            format='json',
        )
        self.assertEqual(refresh_after.status_code, 200)


class LongLivedRefreshTokenTestCase(WgerTestCase):
    """
    Mint, list, and revoke long-lived headless JWT refresh tokens from the
    /user/api-key page.
    """

    def test_generate_shows_token_once(self):
        """
        POST ``new_refresh_token`` mints a token and the next page render
        displays it exactly once. Refreshing the page does not show it again.
        """
        self.user_login('test')

        response = self.client.post(
            reverse('core:user:api-key'),
            {'new_refresh_token': 'true'},
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(response['Location'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Copy this token now.')
        self.assertContains(response, 'Revoke')

        # Refreshing must not show the token again.
        response = self.client.get(reverse('core:user:api-key'))
        self.assertNotContains(response, 'Copy this token now.')

    def test_generated_token_works_against_headless_refresh(self):
        """
        The minted refresh token actually validates against the headless
        token-refresh endpoint and returns a new access token.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        token = mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)

        api = APIClient()
        response = api.post(
            reverse('headless:app:tokens:refresh'),
            data=json.dumps({'refresh_token': token}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        self.assertIn('access_token', body['data'])

    def test_refresh_for_session_without_user_is_rejected(self):
        """
        A refresh token whose session no longer resolves to a user (here: a
        password change rotates the session auth hash) is rejected with a 4xx
        instead of raising a 500.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        token = mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)

        user.set_password('a-different-password')
        user.save()

        api = APIClient()
        response = api.post(
            reverse('headless:app:tokens:refresh'),
            data=json.dumps({'refresh_token': token}),
            content_type='application/json',
        )
        self.assertGreaterEqual(response.status_code, 400)
        self.assertLess(response.status_code, 500)

    @override_settings(SESSION_ENGINE='django.contrib.sessions.backends.cached_db')
    def test_refresh_works_under_cache_backed_engine(self):
        """
        With the production-style cache-backed engine, the DB-persisted session
        is still resolved on refresh (via the engine's DB fallback) and returns a
        new access token.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        token = mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)

        api = APIClient()
        response = api.post(
            reverse('headless:app:tokens:refresh'),
            data=json.dumps({'refresh_token': token}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn('access_token', response.json()['data'])

    @override_settings(SESSION_ENGINE='django.contrib.sessions.backends.cache')
    def test_refresh_fails_under_pure_cache_engine(self):
        """
        A pure-cache session engine cannot read the DB-persisted long-lived
        session, so refresh is rejected. This pins down why the feature requires
        a DB-backed engine in production.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        token = mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)

        api = APIClient()
        response = api.post(
            reverse('headless:app:tokens:refresh'),
            data=json.dumps({'refresh_token': token}),
            content_type='application/json',
        )
        self.assertGreaterEqual(response.status_code, 400)

    def test_revoke_invalidates_token(self):
        """
        Revoking a long-lived session breaks the matching refresh token.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        token = mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)
        sessions = list_long_lived_sessions(user)
        self.assertEqual(len(sessions), 1)
        session_key = sessions[0].session_key

        response = self.client.post(
            reverse('core:user:api-key'),
            {'revoke_refresh_token': session_key},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list_long_lived_sessions(user), [])

        api = APIClient()
        refresh = api.post(
            reverse('headless:app:tokens:refresh'),
            data=json.dumps({'refresh_token': token}),
            content_type='application/json',
        )
        self.assertGreaterEqual(refresh.status_code, 400)

    def test_revoke_all(self):
        """
        Bulk revocation kills every long-lived session of the current user.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        for _ in range(3):
            mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)
        self.assertEqual(len(list_long_lived_sessions(user)), 3)

        response = self.client.post(
            reverse('core:user:api-key'),
            {'revoke_all_refresh_tokens': 'true'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list_long_lived_sessions(user), [])

    def test_revoke_cannot_target_other_users_session(self):
        """
        Posting another user's session_key must not delete that user's
        long-lived session — same cross-user defense as the JWT-revoke flow.
        """
        admin = User.objects.get(username='admin')
        mint_long_lived_refresh_token(admin, lifetime_seconds=120 * 86400)
        admin_sessions = list_long_lived_sessions(admin)
        self.assertEqual(len(admin_sessions), 1)
        admin_session_key = admin_sessions[0].session_key

        self.user_login('test')
        response = self.client.post(
            reverse('core:user:api-key'),
            {'revoke_refresh_token': admin_session_key},
        )
        self.assertEqual(response.status_code, 302)

        # Admin's long-lived session is still there.
        self.assertEqual(len(list_long_lived_sessions(admin)), 1)

    def test_generate_requires_post(self):
        """
        State-changing actions must not be triggered by a GET (CSRF defense).
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        response = self.client.get(
            reverse('core:user:api-key'),
            {'new_refresh_token': 'true'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list_long_lived_sessions(user), [])

    def test_browser_session_is_not_listed(self):
        """
        The user's regular browser session must not show up in the list of
        long-lived refresh tokens — only sessions tagged with
        ``LONG_LIVED_FLAG`` count.
        """
        self.user_login('test')
        user = User.objects.get(username='test')

        # The login above created a browser session; confirm it exists and is
        # *not* listed (no long-lived marker).
        self.assertEqual(list_long_lived_sessions(user), [])

        # And the marker really is what gates inclusion.
        browser_sessions = [
            s for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == str(user.pk)
        ]
        self.assertTrue(browser_sessions)
        for s in browser_sessions:
            self.assertFalse(s.get_decoded().get(LONG_LIVED_FLAG))

    def test_flush_expired_long_lived_sessions_task(self):
        """
        The periodic cleanup task deletes expired DB-backed long-lived sessions
        and their index rows, while leaving still-valid ones untouched.
        """
        user = User.objects.get(username='test')

        before = set(Session.objects.values_list('session_key', flat=True))
        mint_long_lived_refresh_token(user, 3600)
        mint_long_lived_refresh_token(user, 3600)
        expired_key, live_key = set(Session.objects.values_list('session_key', flat=True)) - before

        # Force one of the two sessions past its expiry.
        Session.objects.filter(session_key=expired_key).update(
            expire_date=timezone.now() - timedelta(days=1),
        )

        flush_expired_long_lived_sessions_task()

        self.assertFalse(Session.objects.filter(session_key=expired_key).exists())
        self.assertTrue(Session.objects.filter(session_key=live_key).exists())

        self.assertFalse(LongLivedSession.objects.filter(session_key=expired_key).exists())
        self.assertTrue(LongLivedSession.objects.filter(session_key=live_key).exists())

    def test_overview_does_not_decode_any_session(self):
        """
        Rendering the overview must not decode session payloads, no matter how
        many sessions of other users are in the table. The dates it shows come
        from the index and from the session row itself.
        """
        admin = User.objects.get(username='admin')
        for _ in range(20):
            mint_long_lived_refresh_token(admin, lifetime_seconds=120 * 86400)

        self.user_login('test')
        user = User.objects.get(username='test')
        mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)
        entry = LongLivedSession.objects.get(user=user)

        decoded = []
        original = Session.get_decoded

        def counting_get_decoded(session):
            decoded.append(session.session_key)
            return original(session)

        with mock.patch.object(Session, 'get_decoded', counting_get_decoded):
            response = self.client.get(reverse('core:user:api-key'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(decoded, [])
        self.assertContains(response, timezone.localtime(entry.created).strftime('%Y-%m-%d %H:%M'))

    def test_deleting_the_user_removes_the_index(self):
        """
        The index rows of a deleted user are removed with them.
        """
        user = User.objects.get(username='test')
        mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)
        self.assertEqual(LongLivedSession.objects.filter(user=user).count(), 1)

        user.delete()
        self.assertEqual(LongLivedSession.objects.count(), 0)

    def test_session_deleted_outside_the_app_is_not_listed(self):
        """
        A session that was removed without going through the revoke views does
        not show up in the overview any more.
        """
        user = User.objects.get(username='test')
        mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)
        session_key = list_long_lived_sessions(user)[0].session_key

        Session.objects.filter(session_key=session_key).delete()

        self.assertEqual(list_long_lived_sessions(user), [])


class LongLivedSessionBackfillTestCase(WgerTestCase):
    """
    Tests the data migration that indexes the sessions created before the index
    existed. The test settings skip migrations, so the function is called with
    the current models instead of the historical ones.
    """

    MIGRATION = 'wger.core.migrations.0028_longlivedsession'

    def index_existing_sessions(self):
        module = importlib.import_module(self.MIGRATION)
        module.index_existing_sessions(Session, LongLivedSession, User)

    def test_existing_sessions_are_indexed(self):
        """
        Long-lived sessions without an index row get one, with the user and the
        creation date taken from the session payload.
        """
        user = User.objects.get(username='test')

        # A regular browser session that must be left alone.
        self.user_login('test')

        mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)
        mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)
        keys = set(LongLivedSession.objects.values_list('session_key', flat=True))
        self.assertEqual(len(keys), 2)

        LongLivedSession.objects.all().delete()
        self.index_existing_sessions()

        self.assertEqual(
            set(LongLivedSession.objects.values_list('session_key', flat=True)),
            keys,
        )
        for entry in LongLivedSession.objects.all():
            data = Session.objects.get(session_key=entry.session_key).get_decoded()
            self.assertEqual(entry.user, user)
            self.assertEqual(entry.created, parse_datetime(data[LONG_LIVED_CREATED_AT]))

    def test_expired_sessions_are_skipped(self):
        """
        Sessions that already expired are not indexed, the cleanup task would
        drop them right away.
        """
        user = User.objects.get(username='test')
        mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)
        session_key = LongLivedSession.objects.get().session_key

        Session.objects.filter(session_key=session_key).update(
            expire_date=timezone.now() - timedelta(days=1),
        )
        LongLivedSession.objects.all().delete()
        self.index_existing_sessions()

        self.assertEqual(LongLivedSession.objects.count(), 0)

    def test_running_twice_does_not_duplicate(self):
        """
        Sessions that are already indexed are not indexed a second time.
        """
        user = User.objects.get(username='test')
        mint_long_lived_refresh_token(user, lifetime_seconds=120 * 86400)

        self.index_existing_sessions()

        self.assertEqual(LongLivedSession.objects.count(), 1)
