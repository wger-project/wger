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
from wger.manager.models import Day
from wger.manager.models import Setting
from wger.manager.models import Set
from wger.manager.models import Schedule
from wger.manager.models import WorkoutLog
from wger.manager.models import WorkoutSession


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
    setting_list = serializers.Field()
    setting_text = serializers.Field()
    comment_list = serializers.Field()


class WorkoutCanonicalFormExerciseSerializer(serializers.Serializer):
    '''
    Serializer for an exercise in the canonical form of a workout
    '''
    obj = SetSerializer()
    exercise_list = WorkoutCanonicalFormExerciseListSerializer()
    has_settings = serializers.BooleanField()
    is_superset = serializers.BooleanField()
    muscles = serializers.Field()


class DayCanonicalFormSerializer(serializers.Serializer):
    '''
    Serializer for a day in the canonical form of a workout
    '''
    obj = DaySerializer()
    set_list = WorkoutCanonicalFormExerciseSerializer(many=True)
    days_of_week = serializers.Field()
    muscles = serializers.Field()


class WorkoutCanonicalFormSerializer(serializers.Serializer):
    '''
    Serializer for the canonical form of a workout
    '''
    obj = WorkoutSerializer()
    muscles = serializers.Field()
    day_list = DayCanonicalFormSerializer(many=True)


#
# Routine Generator
#

class RoutineConfigSerializer(serializers.Serializer):
    '''
    Serializer for the configuration options of a workout
    '''
    round_to = serializers.FloatField()
    max_bench = serializers.FloatField()
    max_deadlift = serializers.FloatField()
    max_squat = serializers.FloatField()
    unit = serializers.CharField()


class RoutineExerciseConfigSerializer(serializers.Serializer):
    '''
    Serializer for the canonical form of a workout
    '''
    week = serializers.IntegerField(source='week')
    day = serializers.IntegerField(source='day')
    set = serializers.IntegerField(source='set')
    unit = serializers.CharField()

    weight = serializers.DecimalField()
    reps = serializers.IntegerField()
    sets = serializers.IntegerField()
    increment_mode = serializers.CharField()
    exercise = serializers.CharField(read_only=True)

    def transform_exercise(self, obj, value):
        '''
        Return the available languages for the exercise
        '''
        out = {}
        mapper = obj['config'].routine_exercise.exercise_mapper.get_all_languages()
        for lang in mapper:
            out[lang] = mapper[lang].pk

        return {'name': unicode(obj['config'].routine_exercise.exercise_mapper),
                'ids': out}
