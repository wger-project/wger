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

from rest_framework import serializers

from wger.manager.models import Workout
from wger.manager.models import Schedule
from wger.manager.models import WorkoutLog
from wger.manager.models import WorkoutSession


class WorkoutSerializer(serializers.ModelSerializer):
    '''
    Workout serializer
    '''

    # canonical_representation = serializers.SerializerMethodField('get_canonical_representation')

    class Meta:
        model = Workout
        exclude = ('user',)

    def get_canonical_representation(self, obj):
        return obj.canonical_representation


class WorkoutSessionSerializer(serializers.ModelSerializer):
    '''
    Workout session serializer
    '''
    class Meta:
        model = WorkoutSession
        exclude = ('user',)


class WorkoutLogSerializer(serializers.ModelSerializer):
    '''
    Workout session serializer
    '''
    class Meta:
        model = WorkoutLog
        exclude = ('user',)


class ScheduleSerializer(serializers.ModelSerializer):
    '''
    Schedule serializer
    '''
    class Meta:
        model = Schedule
        exclude = ('user',)
