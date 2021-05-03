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

# Third Party
from rest_framework import serializers

# wger
from wger.core.api.serializers import DaysOfWeekSerializer
from wger.exercises.api.serializers import (
    ExerciseSerializer,
    MuscleSerializer
)
from wger.manager.models import (
    Day,
    Schedule,
    ScheduleStep,
    Set,
    Setting,
    Workout,
    WorkoutLog,
    WorkoutSession
)


class WorkoutSerializer(serializers.ModelSerializer):
    """
    Workout serializer
    """

    class Meta:
        model = Workout
        exclude = ('user',)


class WorkoutSessionSerializer(serializers.ModelSerializer):
    """
    Workout session serializer
    """
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = WorkoutSession
        fields = ['id', 'user', 'workout', 'date', 'notes', 'impression', 'time_start', 'time_end']


class WorkoutLogSerializer(serializers.ModelSerializer):
    """
    Workout session serializer
    """
    class Meta:
        model = WorkoutLog
        exclude = ('user',)


class ScheduleStepSerializer(serializers.ModelSerializer):
    """
    ScheduleStep serializer
    """
    class Meta:
        model = ScheduleStep
        fields = ['id',
                  'schedule',
                  'workout',
                  'duration']


class ScheduleSerializer(serializers.ModelSerializer):
    """
    Schedule serializer
    """
    class Meta:
        model = Schedule
        exclude = ('user',)


class DaySerializer(serializers.ModelSerializer):
    """
    Workout day serializer
    """

    class Meta:
        model = Day
        fields = ['id', 'training', 'description', 'day']


class SetSerializer(serializers.ModelSerializer):
    """
    Workout setting serializer
    """

    class Meta:
        model = Set
        fields = ['id', 'exerciseday', 'sets', 'order']


class SettingSerializer(serializers.ModelSerializer):
    """
    Workout setting serializer
    """
    class Meta:
        model = Setting
        fields = ['id', 'set', 'exercise', 'repetition_unit', 'reps',
                  'weight', 'weight_unit', 'rir', 'order', 'comment']


#
# Custom helper serializers for the canonical form of a workout
#
class MusclesCanonicalFormSerializer(serializers.Serializer):
    """
    Serializer for the muscles in the canonical form of a day/workout
    """
    front = serializers.ListField(child=MuscleSerializer())
    back = serializers.ListField(child=MuscleSerializer())
    frontsecondary = serializers.ListField(child=MuscleSerializer())
    backsecondary = serializers.ListField(child=MuscleSerializer())


class WorkoutCanonicalFormExerciseImagesListSerializer(serializers.Serializer):
    """
    Serializer for settings in the canonical form of a workout
    """
    image = serializers.ReadOnlyField()
    is_main = serializers.ReadOnlyField()


class WorkoutCanonicalFormExerciseListSerializer(serializers.Serializer):
    """
    Serializer for settings in the canonical form of a workout
    """
    setting_obj_list = SettingSerializer(many=True)
    setting_list = serializers.ReadOnlyField()
    setting_text = serializers.ReadOnlyField()
    reps_list = serializers.ReadOnlyField()
    has_weight = serializers.ReadOnlyField()
    weight_list = serializers.ReadOnlyField()
    comment_list = serializers.ReadOnlyField()
    image_list = WorkoutCanonicalFormExerciseImagesListSerializer(many=True)
    obj = ExerciseSerializer()


class WorkoutCanonicalFormExerciseSerializer(serializers.Serializer):
    """
    Serializer for an exercise in the canonical form of a workout
    """
    obj = SetSerializer()
    exercise_list = WorkoutCanonicalFormExerciseListSerializer(many=True)
    is_superset = serializers.BooleanField()
    settings_computed = SettingSerializer(many=True)
    muscles = MusclesCanonicalFormSerializer()


class DaysOfWeekCanonicalFormSerializer(serializers.Serializer):
    """
    Serializer for a days of week in the canonical form of a workout
    """
    text = serializers.ReadOnlyField()
    day_list = serializers.ListField(
        child=DaysOfWeekSerializer()
    )


class DayCanonicalFormSerializer(serializers.Serializer):
    """
    Serializer for a day in the canonical form of a workout
    """
    obj = DaySerializer()
    set_list = WorkoutCanonicalFormExerciseSerializer(many=True)
    days_of_week = DaysOfWeekCanonicalFormSerializer()
    muscles = MusclesCanonicalFormSerializer()


class WorkoutCanonicalFormSerializer(serializers.Serializer):
    """
    Serializer for the canonical form of a workout
    """
    obj = WorkoutSerializer()
    day_list = DayCanonicalFormSerializer(many=True)
    muscles = MusclesCanonicalFormSerializer()
