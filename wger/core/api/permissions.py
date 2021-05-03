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
from rest_framework.permissions import BasePermission


class AllowRegisterUser(BasePermission):
    """
    Checks that users are allow to register via API.

    Apps can register user via the REST API, but only if they have been whitelisted first
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        return request.user.userprofile.can_add_user
