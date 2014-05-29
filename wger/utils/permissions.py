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

from rest_framework import permissions


class WgerPermission(permissions.BasePermission):
    '''
    Checks that the user has access to the object

    If the object has a 'owner_object' method, only allow access for the owner
    user. For the other objects (system wide objects like exercises, etc.) allow
    only safe methods (GET, HEAD or OPTIONS)
    '''

    def has_object_permission(self, request, view, obj):
        '''
        Perform the check
        '''
        owner_object = obj.get_owner_object() if hasattr(obj, 'get_owner_object') else False

        # Owner
        if owner_object and owner_object.user == request.user:
            return True

        # 'global' objects only for GET, HEAD or OPTIONS
        if not owner_object and request.method in permissions.SAFE_METHODS:
            return True

        # Everything else is a no-no
        return False