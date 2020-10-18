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

# Third Party
from rest_framework.authtoken.models import Token


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
