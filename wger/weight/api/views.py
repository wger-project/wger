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

from rest_framework import viewsets
from wger.weight.api.serializers import WeightEntrySerializer

from wger.weight.models import WeightEntry


class WeightEntryViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for nutrition plan objects
    '''
    serializer_class = WeightEntrySerializer
    is_private = True
    ordering_fields = '__all__'
    filter_fields = ('date',
                     'weight')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return WeightEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        '''
        Set the owner
        '''
        serializer.save(user=self.request.user)
