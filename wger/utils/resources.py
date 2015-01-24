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

import logging

from tastypie.authorization import ReadOnlyAuthorization

logger = logging.getLogger(__name__)


class UserObjectsOnlyAuthorization(ReadOnlyAuthorization):
    '''
    Custom authorization class to limit the user's access to his own objects
    '''

    def read_detail(self, object_list, bundle):

        # For models such as userprofile where we don't have an owner function
        if hasattr(bundle.obj, 'user'):
            return bundle.obj.user == bundle.request.user

        try:
            return bundle.obj.get_owner_object().user == bundle.request.user
        # Objects without owner information can be accessed
        except AttributeError:
            return True
