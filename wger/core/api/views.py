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

from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from wger.core.models import UserProfile
from wger.core.models import Language
from wger.core.models import DaysOfWeek
from wger.core.models import License
from wger.core.api.serializers import UsernameSerializer, LanguageSerializer, \
    DaysOfWeekSerializer, LicenseSerializer
from wger.core.api.serializers import UserprofileSerializer
from wger.utils.permissions import UpdateOnlyPermission
from wger.utils.permissions import WgerPermission


class UserProfileViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for workout objects
    '''
    is_private = True
    serializer_class = UserprofileSerializer
    permission_classes = (WgerPermission, UpdateOnlyPermission)
    ordering_fields = '__all__'

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return UserProfile.objects.filter(user=self.request.user)

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [(User, 'user')]

    @detail_route()
    def username(self, request, pk):
        '''
        Return the username
        '''

        user = self.get_object().user
        return Response(UsernameSerializer(user).data)


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for workout objects
    '''
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    ordering_fields = '__all__'
    filter_fields = ('full_name',
                     'short_name')


class DaysOfWeekViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for workout objects
    '''
    queryset = DaysOfWeek.objects.all()
    serializer_class = DaysOfWeekSerializer
    ordering_fields = '__all__'
    filter_fields = ('day_of_week', )


class LicenseViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for workout objects
    '''
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    ordering_fields = '__all__'
    filter_fields = ('full_name',
                     'short_name',
                     'url')
