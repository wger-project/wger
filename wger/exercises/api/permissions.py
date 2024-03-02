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


class CanContributeExercises(BasePermission):
    """
    Checks that users are allowed to create or edit an exercise.

    Regular users that are "trustworthy" (see Userprofile model for details) and
    administrator users with the appropriate exercise permission are allowed to
    perform CRUD operations

    TODO: at the moment the "exercises.delete_exercise" is hard coded here
          and while it is enough and works, ideally we would want to set the
          individual permissions for e.g. aliases or videos.
    """

    SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
    ADD_METHODS = ['POST', 'PUT', 'PATCH']
    DELETE_METHODS = ['DELETE']

    def has_permission(self, request, view):
        # Everybody can read
        if request.method in self.SAFE_METHODS:
            return True

        # Only logged-in users can perform CRUD operations
        if not request.user.is_authenticated:
            return False

        # Creating or updating
        if request.method in self.ADD_METHODS:
            return request.user.userprofile.is_trustworthy or request.user.has_perm(
                'exercises.add_exercise'
            )

        # Only admins are allowed to delete entries
        if request.method in self.DELETE_METHODS:
            return request.user.has_perm('exercises.delete_exercise')
