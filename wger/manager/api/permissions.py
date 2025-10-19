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
from rest_framework import permissions


class RoutinePermission(permissions.BasePermission):
    """
    Custom routine permissions
    """

    def has_permission(self, request, view):
        """Only allow access to authenticated users"""

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        If the routine is a public template, allow read-only access for everyone.
        Otherwise, only the user who created the routine has access.
        """
        if obj.user == request.user:
            return True

        if obj.is_template:
            return request.method in permissions.SAFE_METHODS

        return False
