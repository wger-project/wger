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
from wger.core.models import DaysOfWeek
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
    SetsConfig,
    Setting,
    Slot,
    SlotConfig,
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
            'next_day',
            'name',
            'description',
            'is_rest',
            'last_day_in_week',
            'need_logs_to_advance',
            'type',
        )


class WeightConfigSerializer(serializers.ModelSerializer):
    """
    Weight Config serializer
    """

    class Meta:
        model = WeightConfig
        fields = (
            'id',
            'slot_config',
            'iteration',
            'value',
            'operation',
            'step',
            'replace',
            'need_log_to_apply',
        )


class RepsConfigSerializer(serializers.ModelSerializer):
    """
    Repetition Config serializer
    """

    class Meta:
        model = RepsConfig
        fields = (
            'id',
            'slot_config',
            'iteration',
            'value',
            'operation',
            'step',
            'replace',
            'need_log_to_apply',
        )


class SetNrConfigSerializer(serializers.ModelSerializer):
    """
    Set Nr config serializer
    """

    class Meta:
        model = SetsConfig
        fields = (
            'id',
            'slot_config',
            'iteration',
            'value',
            'operation',
            'step',
            'replace',
        )


class RiRConfigSerializer(serializers.ModelSerializer):
    """
    RiR Config serializer
    """

    class Meta:
        model = RiRConfig
        fields = (
            'id',
            'slot_config',
            'iteration',
            'value',
            'operation',
            'step',
            'replace',
        )


class RestConfigSerializer(serializers.ModelSerializer):
    """
    Rest Config serializer
    """

    class Meta:
        model = RestConfig
        fields = (
            'id',
            'slot_config',
            'iteration',
            'value',
            'operation',
            'step',
            'replace',
        )


class SlotConfigSerializer(serializers.ModelSerializer):
    """
    Slot configuration
    """

    weight_configs = WeightConfigSerializer(source='weightconfig_set', many=True)
    reps_configs = RepsConfigSerializer(source='repsconfig_set', many=True)
    set_nr_configs = SetNrConfigSerializer(source='setsconfig_set', many=True)
    rir_configs = RiRConfigSerializer(source='rirconfig_set', many=True)
    rest_configs = RestConfigSerializer(source='restconfig_set', many=True)

    class Meta:
        model = SlotConfig
        fields = (
            'id',
            'slot',
            'exercise',
            'repetition_unit',
            'repetition_rounding',
            'weight_unit',
            'weight_rounding',
            'order',
            'comment',
            'type',
            'class_name',
            'weight_configs',
            'reps_configs',
            'set_nr_configs',
            'rir_configs',
            'rest_configs',
        )


class SlotSerializer(serializers.ModelSerializer):
    """
    Slot
    """

    configs = SlotConfigSerializer(many=True)

    class Meta:
        model = Slot
        fields = (
            'id',
            'day',
            'order',
            'comment',
            'configs',
        )


class DayStructureSerializer(serializers.ModelSerializer):
    """
    Day serializer
    """

    slots = SlotSerializer(many=True)

    class Meta:
        model = DayNg
        fields = (
            'id',
            'next_day',
            'name',
            'description',
            'is_rest',
            'last_day_in_week',
            'need_logs_to_advance',
            'slots',
        )


class RoutineStructureSerializer(serializers.ModelSerializer):
    """
    Routine structure serializer
    """

    days = DayStructureSerializer(many=True)

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
            'days',
        )


class SetConfigSerializer(serializers.ModelSerializer):
    """
    Day serializer
    """

    class Meta:
        model = SlotConfig
        fields = (
            'id',
            'slot',
            'exercise',
            'type',
            'repetition_unit',
            'repetition_rounding',
            'weight_unit',
            'weight_rounding',
            'order',
            'comment',
            'class_name',
        )


class SetConfigDataSerializer(serializers.Serializer):
    """
    SetConfigData serializer
    """

    slot_config_id = serializers.IntegerField()
    exercise = serializers.IntegerField()
    sets = serializers.IntegerField()
    weight = serializers.DecimalField(max_digits=5, decimal_places=2)
    max_weight = serializers.DecimalField(max_digits=5, decimal_places=2)
    weight_unit = serializers.IntegerField()
    weight_rounding = serializers.DecimalField(max_digits=4, decimal_places=2)
    reps = serializers.DecimalField(max_digits=5, decimal_places=2)
    max_reps = serializers.DecimalField(max_digits=5, decimal_places=2)
    reps_unit = serializers.IntegerField()
    reps_rounding = serializers.DecimalField(max_digits=4, decimal_places=2)
    rir = serializers.DecimalField(max_digits=5, decimal_places=2)
    rpe = serializers.DecimalField(max_digits=5, decimal_places=2)
    rest = serializers.DecimalField(max_digits=5, decimal_places=2)
    max_rest = serializers.DecimalField(max_digits=5, decimal_places=2)
    type = serializers.CharField()
    text_repr = serializers.CharField()
    comment = serializers.CharField()


class SlotDataSerializer(serializers.Serializer):
    """
    Slot Data serializer
    """

    comment = serializers.CharField()
    is_superset = serializers.BooleanField()
    exercises = serializers.ListSerializer(child=serializers.IntegerField())
    sets = SetConfigDataSerializer(many=True)


class WorkoutDayDataDisplayModeSerializer(serializers.Serializer):
    """
    WorkoutDayData serializer - display mode
    """

    iteration = serializers.IntegerField()
    date = serializers.DateField()
    label = serializers.CharField()
    day = DayNgSerializer()
    slots = SlotDataSerializer(many=True, source='slots_display_mode')


class WorkoutDayDataGymModeSerializer(serializers.Serializer):
    """
    WorkoutDayData serializer - gym mode
    """

    iteration = serializers.IntegerField()
    date = serializers.DateField()
    label = serializers.CharField()
    day = DayNgSerializer()
    slots = SlotDataSerializer(many=True, source='slots_gym_mode')


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
