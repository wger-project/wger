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

from wger.core.api.serializers import (
    DaysOfWeekSerializer,
    RepetitionUnitSerializer,
    WeightUnitSerializer
)
from wger.exercises.api.serializers import ExerciseSerializer

from wger.manager.models import (
    Workout,
    ScheduleStep,
    Day,
    Setting,
    Set,
    Schedule,
    WorkoutLog,
    WorkoutSession
)


class WorkoutSerializer(serializers.ModelSerializer):
    '''
    Workout serializer
    '''

    class Meta:
        model = Workout
        exclude = ('user',)


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


class ScheduleStepSerializer(serializers.ModelSerializer):
    '''
    ScheduleStep serializer
    '''
    class Meta:
        model = ScheduleStep


class ScheduleSerializer(serializers.ModelSerializer):
    '''
    Schedule serializer
    '''
    class Meta:
        model = Schedule
        exclude = ('user',)


class DaySerializer(serializers.ModelSerializer):
    '''
    Workout day serializer
    '''

    class Meta:
        model = Day


class SetSerializer(serializers.ModelSerializer):
    '''
    Workout setting serializer
    '''

    class Meta:
        model = Set


class SettingSerializer(serializers.ModelSerializer):
    '''
    Workout setting serializer
    '''
    class Meta:
        model = Setting


#
# Custom helper serializers for the canonical form of a workout
#
class WorkoutCanonicalFormExerciseListSerializer(serializers.Serializer):
    '''
    Serializer for settings in the canonical form of a workout
    '''
    setting_obj_list = SettingSerializer(many=True)
    setting_list = serializers.ReadOnlyField()
    reps_list = serializers.ReadOnlyField()
    has_weight = serializers.ReadOnlyField()
    weight_list = serializers.ReadOnlyField()
    setting_text = serializers.ReadOnlyField()
    repetition_units = RepetitionUnitSerializer(many=True)
    weight_units = WeightUnitSerializer(many=True)
    comment_list = serializers.ReadOnlyField()
    obj = ExerciseSerializer()


class WorkoutCanonicalFormExerciseSerializer(serializers.Serializer):
    '''
    Serializer for an exercise in the canonical form of a workout
    '''
    obj = SetSerializer()
    exercise_list = WorkoutCanonicalFormExerciseListSerializer(many=True)
    has_settings = serializers.BooleanField()
    is_superset = serializers.BooleanField()
    muscles = serializers.ReadOnlyField()


class DaysOfWeekCanonicalFormSerializer(serializers.Serializer):
    '''
    Serializer for a days of week in the canonical form of a workout
    '''
    text = serializers.ReadOnlyField()
    day_list = serializers.ListField(
        child=DaysOfWeekSerializer()
    )


class DayCanonicalFormSerializer(serializers.Serializer):
    '''
    Serializer for a day in the canonical form of a workout
    '''
    obj = DaySerializer()
    set_list = WorkoutCanonicalFormExerciseSerializer(many=True)
    days_of_week = DaysOfWeekCanonicalFormSerializer()
    muscles = serializers.ReadOnlyField()


class WorkoutCanonicalFormSerializer(serializers.Serializer):
    '''
    Serializer for the canonical form of a workout
    '''
    obj = WorkoutSerializer()
    muscles = serializers.ReadOnlyField()
    day_list = DayCanonicalFormSerializer(many=True)
