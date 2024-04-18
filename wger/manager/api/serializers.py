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
from wger.core.models import DaysOfWeek
from wger.exercises.api.serializers import (
    ExerciseBaseInfoSerializer,
    MuscleSerializer,
)
from wger.manager.models import (
    Day,
    DayNg,
    RepsConfig,
    RestConfig,
    RiRConfig,
    Routine,
    Schedule,
    ScheduleStep,
    Set,
    SetConfig,
    SetNg,
    Setting,
    WeightConfig,
    Workout,
    WorkoutLog,
    WorkoutSession,
)


class RoutineSerializer(serializers.ModelSerializer):
    """
    Routine serializer
    """

    class Meta:
        model = Routine
        fields = (
            'id',
            'name',
            'description',
            'first_day',
            'created',
            'start',
            'end',
        )


class DayNgSerializer(serializers.ModelSerializer):
    """
    Day serializer
    """

    class Meta:
        model = DayNg
        fields = (
            'id',
            'name',
            'description',
            'is_rest',
            'need_logs_to_advance',
            'next_day',
        )


class SetNgSerializer(serializers.ModelSerializer):
    """
    SetNg
    """

    class Meta:
        model = SetNg
        fields = (
            'id',
            'day',
            'order',
            'comment',
            'is_dropset',
        )


class SetConfigSerializer(serializers.ModelSerializer):
    """
    Day serializer
    """

    class Meta:
        model = SetConfig
        fields = (
            'id',
            'set',
            'exercise',
            'repetition_unit',
            'weight_unit',
            'order',
            'comment',
            'class_name',
        )


class WeightConfigSerializer(serializers.ModelSerializer):
    """
    Weight Config serializer
    """

    class Meta:
        model = WeightConfig
        fields = (
            'set_config',
            'iteration',
            'trigger',
            'value',
            'operation',
            'step',
            'replace',
            'need_log_to_apply',
        )


class RepetitionConfigSerializer(serializers.ModelSerializer):
    """
    Repetition Config serializer
    """

    class Meta:
        model = RepsConfig
        fields = (
            'set_config',
            'iteration',
            'trigger',
            'value',
            'operation',
            'step',
            'replace',
            'need_log_to_apply',
        )


class RiRConfigSerializer(serializers.ModelSerializer):
    """
    RiR Config serializer
    """

    class Meta:
        model = RiRConfig
        fields = (
            'set_config',
            'iteration',
            'trigger',
            'value',
            'operation',
            'step',
            'replace',
            'need_log_to_apply',
        )


class RestConfigSerializer(serializers.ModelSerializer):
    """
    Rest Config serializer
    """

    class Meta:
        model = RestConfig
        fields = (
            'set_config',
            'iteration',
            'trigger',
            'value',
            'operation',
            'step',
            'replace',
            'need_log_to_apply',
        )


class SetConfigDataSerializer(serializers.Serializer):
    """
    SetData serializer
    """

    sets = serializers.IntegerField()
    weight = serializers.DecimalField(max_digits=5, decimal_places=2)
    weight_unit = serializers.IntegerField()
    weight_rounding = serializers.DecimalField(max_digits=4, decimal_places=2)
    reps = serializers.DecimalField(max_digits=5, decimal_places=2)
    reps_unit = serializers.IntegerField()
    reps_rounding = serializers.DecimalField(max_digits=4, decimal_places=2)
    rir = serializers.DecimalField(max_digits=5, decimal_places=2)
    rest = serializers.DecimalField(max_digits=5, decimal_places=2)


class SetExerciseDataSerializer(serializers.Serializer):
    """
    SetData serializer
    """

    # exercise = ExerciseBaseInfoSerializer()
    data = SetConfigDataSerializer()
    config = SetConfigSerializer()


class SetDataSerializer(serializers.Serializer):
    """
    SetData serializer
    """

    set = SetNgSerializer()
    exercise_data = SetExerciseDataSerializer(many=True)


class WorkoutDayDataSerializer(serializers.Serializer):
    """
    WorkoutDayData serializer
    """

    iteration = serializers.IntegerField()
    date = serializers.DateField()
    day = DayNgSerializer()
    sets = SetDataSerializer(many=True)


class WorkoutSerializer(serializers.ModelSerializer):
    """
    Workout serializer
    """

    class Meta:
        model = Workout
        fields = ('id', 'name', 'creation_date', 'description')


class WorkoutTemplateSerializer(serializers.ModelSerializer):
    """
    Workout template serializer
    """

    class Meta:
        model = Workout
        fields = ('id', 'name', 'creation_date', 'description', 'is_public')


class WorkoutSessionSerializer(serializers.ModelSerializer):
    """
    Workout session serializer
    """

    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = WorkoutSession
        fields = [
            'id',
            'user',
            'workout',
            'date',
            'notes',
            'impression',
            'time_start',
            'time_end',
        ]


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
        fields = ['id', 'schedule', 'workout', 'duration']


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

    training = serializers.PrimaryKeyRelatedField(queryset=Workout.objects.all())
    day = serializers.PrimaryKeyRelatedField(queryset=DaysOfWeek.objects.all(), many=True)

    class Meta:
        model = Day
        fields = ['id', 'training', 'description', 'day']


class SetSerializer(serializers.ModelSerializer):
    """
    Workout setting serializer
    """

    exerciseday = serializers.PrimaryKeyRelatedField(queryset=Day.objects.all())

    class Meta:
        model = Set
        fields = ['id', 'exerciseday', 'sets', 'order', 'comment']


class SettingSerializer(serializers.ModelSerializer):
    """
    Workout setting serializer
    """

    class Meta:
        model = Setting
        fields = [
            'id',
            'set',
            'exercise_base',
            'repetition_unit',
            'reps',
            'weight',
            'weight_unit',
            'rir',
            'order',
            'comment',
        ]
