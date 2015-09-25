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

from tastypie.authentication import ApiKeyAuthentication
from tastypie.constants import ALL
from tastypie.resources import ModelResource

from wger.utils.resources import UserObjectsOnlyAuthorization
from wger.core.models import (
    UserProfile,
    Language,
    DaysOfWeek,
    License
)


class UserProfileResource(ModelResource):
    '''
    Resource for user profiles
    '''

    def authorized_read_list(self, object_list, bundle):
        '''
        Filter to own objects
        '''
        return object_list.filter(user=bundle.request.user)

    class Meta:
        excludes = ('is_temporary', )
        queryset = UserProfile.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()


class LanguageResource(ModelResource):
    '''
    Resource for languages
    '''
    class Meta:
        queryset = Language.objects.all()
        filtering = {'id': ALL,
                     "full_name": ALL,
                     "short_name": ALL}


class DaysOfWeekResource(ModelResource):
    '''
    Resource for days of the week
    '''

    class Meta:
        queryset = DaysOfWeek.objects.all()
        filtering = {'id': ALL,
                     'day_of_week': ALL}


class LicenseResource(ModelResource):
    '''
    Resource for licenses
    '''
    class Meta:
        queryset = License.objects.all()
        filtering = {'id': ALL,
                     "full_name": ALL,
                     "short_name": ALL,
                     "url": ALL}
