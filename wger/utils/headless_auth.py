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

# Third Party
from allauth.headless.contrib.rest_framework.authentication import JWTTokenAuthentication
from allauth.headless.tokens.strategies.jwt import internal
from allauth.headless.tokens.strategies.jwt.strategy import JWTTokenStrategy
from rest_framework.exceptions import AuthenticationFailed


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
            return super().authenticate(request)
        except AuthenticationFailed:
            return None


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
    """

    def refresh_token(self, refresh_token: str) -> tuple[str, str] | None:
        validated = internal.validate_refresh_token(refresh_token)
        if validated is None or validated[0] is None:
            return None
        return super().refresh_token(refresh_token)
