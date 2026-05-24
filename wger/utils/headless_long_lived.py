# -*- coding: utf-8 -*-

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

"""
Long-lived refresh tokens for the headless JWT surface.

Headless JWT refresh tokens reference a Django session row via an encrypted
``sid`` claim. Normal app logins reuse the user's session, which means
clearing cookies / web logout / session expiry kills the token. For scripts
and CLI tools we want a token that survives those events, so we mint a
dedicated session row, mark it, and back the refresh token by that.
"""

# Django
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
)
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.utils import timezone


# Marker stored on the session payload to identify long-lived sessions later.
LONG_LIVED_FLAG = 'wger_long_lived_refresh'
LONG_LIVED_CREATED_AT = 'wger_long_lived_refresh_created_at'

# Backend wired in settings_global.py used for sessions created outside the
# request/response cycle, where ``user.backend`` isn't set by Django's login().
_DEFAULT_BACKEND = 'allauth.account.auth_backends.AuthenticationBackend'


def mint_long_lived_refresh_token(user, lifetime_seconds: int) -> str:
    """
    Create a dedicated Django session row for *user* and return a headless
    JWT refresh token backed by it. The session is independent of the user's
    browser session and is tagged so it can be listed/revoked from the web UI.
    """

    # Imported lazily to avoid a hard dependency on the headless app at import
    # time (lets self-hosters with headless disabled still import this module).
    from allauth.headless.tokens.strategies.jwt.internal import create_refresh_token

    backend = getattr(user, 'backend', None) or _DEFAULT_BACKEND
    session = SessionStore()
    session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    session[BACKEND_SESSION_KEY] = backend
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    session[LONG_LIVED_FLAG] = True
    session[LONG_LIVED_CREATED_AT] = timezone.now().isoformat()
    session.set_expiry(lifetime_seconds)

    # Initial save assigns the session_key that create_refresh_token needs to
    # build the JWT's ``sid`` claim.
    session.save()
    token = create_refresh_token(user, session)

    # create_refresh_token records the new ``jti`` in the session payload
    # (under ``headless_refresh_tokens``) but does not persist; without this
    # second save, /tokens/refresh would not find the jti and reject the
    # token as unknown.
    session.save()
    return token


def list_long_lived_sessions(user):
    """
    Iterate over the unexpired long-lived sessions belonging to *user*. Yields
    ``Session`` model instances, sorted by creation time (newest first).
    """
    user_id = str(user.pk)
    rows = []
    for s in Session.objects.filter(expire_date__gt=timezone.now()):
        try:
            data = s.get_decoded()
        except Exception:
            # A corrupted session row should not break the page. Django's
            # signed_cookies/db backends both protect against tampering, so
            # decode failures only happen for legitimate edge cases (e.g. a
            # cleared SECRET_KEY across deployments).
            continue
        if data.get(SESSION_KEY) != user_id:
            continue
        if not data.get(LONG_LIVED_FLAG):
            continue
        rows.append((s, data.get(LONG_LIVED_CREATED_AT) or ''))
    rows.sort(key=lambda row: row[1], reverse=True)
    return [row[0] for row in rows]


def revoke_long_lived_session(user, session_key: str) -> bool:
    """
    Delete a single long-lived session by key, but only when it actually
    belongs to *user* and is marked long-lived. Returns ``True`` if a row was
    deleted.
    """
    try:
        s = Session.objects.get(
            session_key=session_key,
            expire_date__gt=timezone.now(),
        )
    except Session.DoesNotExist:
        return False
    data = s.get_decoded()
    if data.get(SESSION_KEY) != str(user.pk):
        return False
    if not data.get(LONG_LIVED_FLAG):
        return False
    s.delete()
    return True


def revoke_all_long_lived_sessions(user) -> int:
    """
    Delete every long-lived session belonging to *user*. Returns the number
    of revoked sessions.
    """
    sessions = list_long_lived_sessions(user)
    Session.objects.filter(session_key__in=[s.session_key for s in sessions]).delete()
    return len(sessions)
