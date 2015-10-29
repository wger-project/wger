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

from rest_framework import exceptions, viewsets


class WgerOwnerObjectModelViewSet(viewsets.ModelViewSet):
    '''
    Custom viewset that makes sure the user can only create objects for himself
    '''
    def create(self, request, *args, **kwargs):
        '''
        Check for creation (PUT, POST)
        '''
        for entry in self.get_owner_objects():
            if request.data.get(entry[1]):
                pk = request.data.get(entry[1])
                obj = entry[0].objects.get(pk=pk)
                if obj.get_owner_object().user != request.user:
                    raise exceptions.PermissionDenied('You are not allowed to do this')
        else:
            return super(WgerOwnerObjectModelViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        '''
        Check for updates (PUT, PATCH)
        '''
        for entry in self.get_owner_objects():
            if request.data.get(entry[1]):
                pk = request.data.get(entry[1])
                obj = entry[0].objects.get(pk=pk)
                if obj.get_owner_object().user != request.user:
                    raise exceptions.PermissionDenied('You are not allowed to do this')
        else:
            return super(WgerOwnerObjectModelViewSet, self).update(request, *args, **kwargs)
