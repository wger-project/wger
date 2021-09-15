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


class CanEditExercises(BasePermission):
    """
    Checks that users are allowed to create or edit an exercise.

    Regular users that are "trustworthy" (see Userprofile model for details) and
    administrator users with the appropriate exercise permission are allowed.
    """
    SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

    def has_permission(self, request, view):

        # Everybody can read
        if request.method in self.SAFE_METHODS:
            return True

        # Only "trustworthy" users can edit
        return (
            request.user.userprofile.is_trustworthy
            or request.user.has_perm('exercises.add_exercise')
        )
