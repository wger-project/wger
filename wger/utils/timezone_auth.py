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

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

# Third Party
from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


def activate_user_timezone(user) -> None:
    """
    Activates the user's timezone for the rest of the request

    TimezoneMiddleware runs before DRF resolves token credentials and only
    sees the session user, so a token-authenticated request would otherwise
    run in the instance zone: the same date filter would answer differently
    depending on how the caller logged in.
    """
    # Best effort, rendering comfort must never break authentication: a JWT
    # can outlive its user's profile
    try:
        timezone.activate(user.userprofile.zone_info)
    except ObjectDoesNotExist:
        timezone.deactivate()


class TimezoneActivationMixin:
    """Activates the authenticated user's timezone, see activate_user_timezone"""

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            activate_user_timezone(result[0])
        return result


class TimezoneTokenAuthentication(TimezoneActivationMixin, TokenAuthentication):
    pass


class TimezoneJWTAuthentication(TimezoneActivationMixin, JWTAuthentication):
    pass


class TimezoneJWTScheme(SimpleJWTScheme):
    """
    Keeps the jwtAuth entry in the schema: the simplejwt extension targets the
    original class and does not match subclasses
    """

    target_class = 'wger.utils.timezone_auth.TimezoneJWTAuthentication'
