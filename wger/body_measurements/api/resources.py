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

# Third Party
from tastypie.authentication import ApiKeyAuthentication
from tastypie.constants import ALL
from tastypie.resources import ModelResource

# wger
from wger.utils.resources import UserObjectsOnlyAuthorization
from wger.body_measurements.models import BodyMeasurementsEntry


class BodyMeasurementsEntryResource(ModelResource):
    '''
    Resource for body measurements entries
    '''

    def authorized_read_list(self, object_list, bundle):
        '''
        Filter to own objects
        '''
        return object_list.filter(user=bundle.request.user)

    class Meta:
        queryset = BodyMeasurementsEntry.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
        filtering = {'id': ALL,
                     'date': ALL,
                     'chest': ALL,
                     'hips': ALL, 
                     'waist': ALL}
