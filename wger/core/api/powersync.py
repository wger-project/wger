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

# Standard Library
import json
import time
from base64 import urlsafe_b64decode
from functools import lru_cache

# Django
from django.conf import settings

# Third Party
import jwt
from jwt.algorithms import RSAAlgorithm


@lru_cache(maxsize=1)
def _private_jwk():
    return json.loads(urlsafe_b64decode(settings.JWT_PRIVATE_KEY))


@lru_cache(maxsize=1)
def _private_key():
    return RSAAlgorithm.from_jwk(json.dumps(_private_jwk()))


@lru_cache(maxsize=1)
def public_jwk():
    return json.loads(urlsafe_b64decode(settings.JWT_PUBLIC_KEY))


def create_token(user_id):
    jwk = _private_jwk()
    now = int(time.time())
    return jwt.encode(
        {
            'sub': str(user_id),
            'iat': now,
            'aud': 'powersync',
            'exp': now + 600,
        },
        _private_key(),
        algorithm=jwk['alg'],
        headers={'kid': jwk['kid']},
    )
