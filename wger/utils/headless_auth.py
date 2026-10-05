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

# Django
from django.contrib.auth import get_user_model

# Third Party
from allauth.headless import app_settings
from allauth.headless.contrib.rest_framework.authentication import JWTTokenAuthentication
from allauth.headless.tokens.strategies.jwt import internal
from allauth.headless.tokens.strategies.jwt.strategy import JWTTokenStrategy
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.exceptions import AuthenticationFailed

# wger
from wger.utils.timezone_auth import activate_user_timezone


# Session key mapping the jti of each not yet used refresh token to the jti of
# the token it replaced
REFRESH_TOKEN_PREDECESSORS = 'wger_refresh_token_predecessors'


class HeadlessJWTAuthentication(JWTTokenAuthentication):
    """
    Lenient variant of allauth's JWTTokenAuthentication.

    Returns ``None`` for tokens that don't validate as a headless JWT instead of
    raising. ``Authorization: Bearer`` is shared with ``rest_framework_simplejwt``
    raising would abort the DRF auth chain and stop the next class from getting a
    chance at the token.
    """

    def authenticate(self, request):
        try:
            result = super().authenticate(request)
        except AuthenticationFailed:
            return None
        if result is not None:
            activate_user_timezone(result[0])
        return result

    def authenticate_credentials(self, key):
        user, payload = super().authenticate_credentials(key)
        # validate_access_token hands back a SimpleLazyObject that only hits the
        # DB on first access. Force the lookup now so an access token whose user
        # was deleted fails as a clean 401 here, instead of raising DoesNotExist
        # later on and raising an uncaught 500.
        try:
            _ = user.pk
        except get_user_model().DoesNotExist as exc:
            raise AuthenticationFailed('Invalid token') from exc

        # allauth loads the user without checking is_active, but deactivation
        # has to lock the account out immediately, not at token expiry
        if not user.is_active:
            raise AuthenticationFailed('User inactive or deleted')

        return user, payload


class HeadlessJWTScheme(OpenApiAuthenticationExtension):
    """
    Schema entry for HeadlessJWTAuthentication.

    Without this, drf-spectacular derives the name from the TokenAuthentication
    base class and collides with DRF's own "tokenAuth", documenting the wrong
    "Token" prefix for this Bearer-based class.
    """

    target_class = 'wger.utils.headless_auth.HeadlessJWTAuthentication'
    name = 'headlessJwtAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'Access token issued by the allauth headless endpoints',
        }


class WgerJWTTokenStrategy(JWTTokenStrategy):
    """
    Hardened variant of allauth's JWTTokenStrategy.

    ``internal.validate_refresh_token`` returns a ``(None, session, payload)``
    tuple when the refresh token and its backing session are valid but the
    session no longer resolves to a user, e.g. after a password change rotates
    the session auth hash, or the user was deleted/deactivated.

    Allauth's ``refresh_token`` logic hands the None-User to ``create_access_token``,
    which asserts ``user.is_authenticated`` and raises a 500. Reject the token
    cleanly instead, so the endpoint answers with the same error a client already
    handles for an expired token.

    Rotation is delayed: a refresh token stays valid until its successor has been
    used once. Allauth drops it immediately, so a response lost on the way to the
    client (timeout, network switch, app suspended) left it without a usable token.
    """

    def refresh_token(self, refresh_token: str) -> tuple[str, str] | None:
        validated = internal.validate_refresh_token(refresh_token)
        if validated is None or validated[0] is None:
            return None
        if not app_settings.JWT_ROTATE_REFRESH_TOKEN:
            return super().refresh_token(refresh_token)

        user, session, payload = validated
        jti = payload['jti']
        predecessors = session.setdefault(REFRESH_TOKEN_PREDECESSORS, {})

        # Using a successor proves it arrived, the token it replaced can go
        predecessor = predecessors.pop(jti, None)
        if predecessor is not None:
            internal.invalidate_refresh_token(session, {'jti': predecessor})

        # A token used again after it was already replaced means that answer never
        # arrived, so the unused successor is dropped in favour of the new one
        for successor, replaced in list(predecessors.items()):
            if replaced == jti:
                del predecessors[successor]
                internal.invalidate_refresh_token(session, {'jti': successor})

        access_token = internal.create_access_token(user, session, self.get_claims(user))
        next_refresh_token = internal.create_refresh_token(user, session)
        next_jti = internal.decode_token(next_refresh_token, 'refresh')['jti']
        predecessors[next_jti] = jti
        session.save()
        return access_token, next_refresh_token
