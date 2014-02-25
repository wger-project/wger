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
from tastypie.exceptions import TastypieError, Unauthorized

logger = logging.getLogger('wger.custom')


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

    def create_detail(self, object_list, bundle):
        ### In what scenario is this method used?  - dashdrum 2/20/2014
        raise TastypieError('create_detail authorization check')
        try:
            return bundle.obj.get_owner_object().user == bundle.request.user
        except AttributeError:
            raise Unauthorized("You are not allowed to access that resource.")

    def update_detail(self, object_list, bundle):
        # Check for an owner_object and compare users
        try:
            return bundle.obj.get_owner_object().user == bundle.request.user
        # Only objects with owner information should use this authorization class
        # Fail authorization attempt if the attribute is not found
        except AttributeError:
            raise Unauthorized("You are not allowed to access that resource.")

    def delete_detail(self, object_list, bundle):
        # Check for an owner_object and compare users
        try:
            return bundle.obj.get_owner_object().user == bundle.request.user
        # Only objects with owner information should use this authorization class
        # Fail authorization attempt if the attribute is not found
        except AttributeError:
            raise Unauthorized("You are not allowed to access that resource.")