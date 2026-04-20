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
from jose.jwt import encode


@lru_cache(maxsize=1)
def _private_jwk():
    return json.loads(urlsafe_b64decode(settings.POWERSYNC_JWKS_PRIVATE_KEY))


@lru_cache(maxsize=1)
def public_jwk():
    return json.loads(urlsafe_b64decode(settings.POWERSYNC_JWKS_PUBLIC_KEY))


def create_token(user_id):
    jwk = _private_jwk()
    return encode(
        {
            'sub': user_id,
            'iat': time.time(),
            'aud': 'powersync',
            'exp': int(time.time()) + 300,
        },
        jwk,
        algorithm=jwk['alg'],
        headers={'alg': jwk['alg'], 'kid': jwk['kid']},
    )
