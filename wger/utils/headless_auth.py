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
