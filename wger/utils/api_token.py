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
import logging

# Django
from django.utils import timezone

# Third Party
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)


logger = logging.getLogger(__name__)


def create_token(user, force_new=False):
    """
    Creates a new token for a user or returns the existing one.

    :param user: User object
    :param force_new: forces creating a new token
    """
    token = False

    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        force_new = True

    if force_new:
        if token:
            token.delete()
        token = Token.objects.create(user=user)

    return token


def _active_jwt_refresh_tokens(user):
    """
    Outstanding refresh tokens for ``user`` that are still usable: not yet
    expired and not already blacklisted.
    """
    return OutstandingToken.objects.filter(
        user=user,
        expires_at__gt=timezone.now(),
        blacklistedtoken__isnull=True,
    )


def count_active_jwt_refresh_tokens(user):
    """
    How many JWT refresh tokens are currently usable for ``user``.
    """
    return _active_jwt_refresh_tokens(user).count()


def blacklist_jwt_refresh_tokens(user):
    """
    Blacklist every outstanding JWT refresh token belonging to ``user``.

    Subsequent calls to ``/api/v2/token/refresh`` with these tokens are
    rejected; the matching access tokens still work until their (much
    shorter) lifetime expires.
    """
    for outstanding in _active_jwt_refresh_tokens(user):
        BlacklistedToken.objects.get_or_create(token=outstanding)
