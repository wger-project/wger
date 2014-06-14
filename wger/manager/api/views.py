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

import datetime

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import link

from wger.manager.api.serializers import WorkoutSerializer
from wger.manager.api.serializers import WorkoutCanonicalFormSerializer
from wger.manager.api.serializers import DaySerializer
from wger.manager.api.serializers import SettingSerializer
from wger.manager.api.serializers import SetSerializer
from wger.manager.api.serializers import ScheduleSerializer
from wger.manager.api.serializers import WorkoutLogSerializer
from wger.manager.api.serializers import WorkoutSessionSerializer

from wger.manager.models import Workout
from wger.manager.models import Set
from wger.manager.models import ScheduleStep
from wger.manager.models import Schedule
from wger.manager.models import Day
from wger.manager.models import Setting
from wger.manager.models import WorkoutLog
from wger.manager.models import WorkoutSession
from wger.utils.viewsets import WgerOwnerObjectModelViewSet


class WorkoutViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for workout objects
    '''
    model = Workout
    serializer_class = WorkoutSerializer
    is_private = True
    filter_fields = ('comment',
                     'creation_date')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return Workout.objects.filter(user=self.request.user)

    def pre_save(self, obj):
        '''
        Set the owner
        '''
        obj.user = self.request.user

    @link()
    def canonical_representation(self, request, pk):
        '''
        Output the canonical representation of a workout

        This is basically the same form as used in the application
        '''

        out = WorkoutCanonicalFormSerializer(self.get_object().canonical_representation).data
        return Response(out)


class WorkoutSessionViewSet(WgerOwnerObjectModelViewSet):
    '''
    API endpoint for workout sessions objects
    '''
    model = WorkoutSession
    serializer_class = WorkoutSessionSerializer
    is_private = True
    filter_fields = ('date',
                     'time_start',
                     'time_end')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return WorkoutSession.objects.filter(user=self.request.user)

    def pre_save(self, obj):
        '''
        Set the owner
        '''
        obj.date = datetime.date.today()  # TODO: actually, this should be editable
        obj.user = self.request.user

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [(Workout, 'workout')]


class ScheduleStepViewSet(WgerOwnerObjectModelViewSet):
    '''
    API endpoint for schedule step objects

    TODO: error while POSTing
          object of type 'int' has no len()
    '''
    model = ScheduleStep
    is_private = True
    ordering_fields = '__all__'
    filter_fields = ('schedule',
                     'workout',
                     'duration',
                     'order')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return ScheduleStep.objects.filter(schedule__user=self.request.user)

    def pre_save(self, obj):
        '''
        Set the order
        '''
        obj.order = 1

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [(Workout, 'workout'),
                (Schedule, 'schedule')]


class ScheduleViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for schedule objects
    '''
    model = Schedule
    serializer_class = ScheduleSerializer
    is_private = True
    filter_fields = ('is_active',
                     'is_loop',
                     'name')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return Schedule.objects.filter(user=self.request.user)

    def pre_save(self, obj):
        '''
        Set the order
        '''
        obj.user = self.request.user


class DayViewSet(WgerOwnerObjectModelViewSet):
    '''
    API endpoint for training day objects
    '''
    model = Day
    serializer_class = DaySerializer
    is_private = True
    filter_fields = ('description',
                     'training',
                     'day')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return Day.objects.filter(training__user=self.request.user)

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [(Workout, 'training')]


class SetViewSet(WgerOwnerObjectModelViewSet):
    '''
    API endpoint for workout set objects
    '''
    model = Set
    serializer_class = SetSerializer
    is_private = True
    filter_fields = ('exerciseday',
                     'order',
                     'sets',
                     'exercises')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return Set.objects.filter(exerciseday__training__user=self.request.user)

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [(Day, 'exerciseday')]


class SettingViewSet(WgerOwnerObjectModelViewSet):
    '''
    API endpoint for repetition setting objects
    '''
    model = Setting
    serializer_class = SettingSerializer
    is_private = True
    filter_fields = ('exercise',
                     'order',
                     'reps',
                     'set',
                     'order')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return Setting.objects.filter(set__exerciseday__training__user=self.request.user)

    def pre_save(self, obj):
        '''
        Set the order
        '''
        obj.order = 1

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [(Set, 'set')]


class WorkoutLogViewSet(WgerOwnerObjectModelViewSet):
    '''
    API endpoint for workout log objects
    '''
    model = WorkoutLog
    serializer_class = WorkoutLogSerializer
    is_private = True
    filter_fields = ('date',
                     'exercise',
                     'reps',
                     'weight',
                     'workout')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''

        return WorkoutLog.objects.filter(user=self.request.user)

    def pre_save(self, obj):
        '''
        Set the order
        '''
        obj.user = self.request.user

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [(Workout, 'workout')]
