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

# Django
from django.apps import apps

# Third Party
from rest_framework import serializers

# wger
from wger.exercises.models import Exercise
from wger.manager.api.consts import BASE_CONFIG_FIELDS
from wger.manager.api.fields import DecimalOrIntegerField
from wger.manager.api.validators import validate_requirements
from wger.manager.models import (
    Day,
    MaxRepetitionsConfig,
    MaxRestConfig,
    MaxRiRConfig,
    MaxSetsConfig,
    MaxWeightConfig,
    RepetitionsConfig,
    RestConfig,
    RiRConfig,
    Routine,
    SetsConfig,
    Slot,
    SlotEntry,
    WeightConfig,
    WorkoutLog,
    WorkoutSession,
)


class ExerciseLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name']


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
            'created',
            'start',
            'end',
            'fit_in_week',
            'is_template',
            'is_public',
        )


class DaySerializer(serializers.ModelSerializer):
    """
    Day serializer
    """

    class Meta:
        model = Day
        fields = (
            'id',
            'routine',
            'order',
            'name',
            'description',
            'is_rest',
            'need_logs_to_advance',
            'type',
            'config',
        )


class BaseConfigSerializer(serializers.ModelSerializer):
    """
    Base Config serializer
    """

    requirements = serializers.JSONField(
        validators=[validate_requirements],
        allow_null=True,
        required=False,
    )


class WeightConfigSerializer(BaseConfigSerializer):
    """
    Weight Config serializer
    """

    class Meta:
        model = WeightConfig
        fields = BASE_CONFIG_FIELDS


class MaxWeightConfigSerializer(BaseConfigSerializer):
    """
    Max Weight Config serializer
    """

    class Meta:
        model = MaxWeightConfig
        fields = BASE_CONFIG_FIELDS


class RepetitionsConfigSerializer(BaseConfigSerializer):
    """
    Repetition Config serializer
    """

    class Meta:
        model = RepetitionsConfig
        fields = BASE_CONFIG_FIELDS


class MaxRepetitionsConfigSerializer(BaseConfigSerializer):
    """
    Max Repetition Config serializer
    """

    class Meta:
        model = MaxRepetitionsConfig
        fields = BASE_CONFIG_FIELDS


class SetNrConfigSerializer(BaseConfigSerializer):
    """
    Set Nr config serializer
    """

    class Meta:
        model = SetsConfig
        fields = BASE_CONFIG_FIELDS


class MaxSetNrConfigSerializer(BaseConfigSerializer):
    """
    Max Set Nr config serializer
    """

    class Meta:
        model = MaxSetsConfig
        fields = BASE_CONFIG_FIELDS


class RiRConfigSerializer(BaseConfigSerializer):
    """
    RiR Config serializer
    """

    class Meta:
        model = RiRConfig
        fields = BASE_CONFIG_FIELDS


class MaxRiRConfigSerializer(BaseConfigSerializer):
    """
    RiR Config serializer
    """

    class Meta:
        model = MaxRiRConfig
        fields = BASE_CONFIG_FIELDS


class RestConfigSerializer(BaseConfigSerializer):
    """
    Rest Config serializer
    """

    class Meta:
        model = RestConfig
        fields = BASE_CONFIG_FIELDS


class MaxRestConfigSerializer(BaseConfigSerializer):
    """
    Rest Config serializer
    """

    class Meta:
        model = MaxRestConfig
        fields = BASE_CONFIG_FIELDS


class SlotEntryStructureSerializer(serializers.ModelSerializer):
    """
    Slot entry
    """

    weight_configs = WeightConfigSerializer(source='weightconfig_set', many=True)
    max_weight_configs = WeightConfigSerializer(source='maxweightconfig_set', many=True)
    repetitions_configs = RepetitionsConfigSerializer(source='repetitionsconfig_set', many=True)
    max_repetitions_configs = RepetitionsConfigSerializer(
        source='maxrepetitionsconfig_set', many=True
    )
    set_nr_configs = SetNrConfigSerializer(source='setsconfig_set', many=True)
    max_set_nr_configs = MaxSetNrConfigSerializer(source='maxsetsconfig_set', many=True)
    rir_configs = RiRConfigSerializer(source='rirconfig_set', many=True)
    max_rir_configs = MaxRiRConfigSerializer(source='maxrirconfig_set', many=True)
    rest_configs = RestConfigSerializer(source='restconfig_set', many=True)
    max_rest_configs = RestConfigSerializer(source='maxrestconfig_set', many=True)

    class Meta:
        model = SlotEntry
        fields = (
            'id',
            'slot',
            'exercise',
            'order',
            'comment',
            'type',
            'class_name',
            'config',
            'repetition_unit',
            'repetition_rounding',
            'repetitions_configs',
            'max_repetitions_configs',
            'weight_unit',
            'weight_rounding',
            'weight_configs',
            'max_weight_configs',
            'set_nr_configs',
            'max_set_nr_configs',
            'rir_configs',
            'max_rir_configs',
            'rest_configs',
            'max_rest_configs',
        )


class SlotStructureSerializer(serializers.ModelSerializer):
    """
    Slot
    """

    entries = SlotEntryStructureSerializer(many=True)

    class Meta:
        model = Slot
        fields = (
            'id',
            'day',
            'order',
            'comment',
            'entries',
            'config',
        )


class SlotSerializer(serializers.ModelSerializer):
    """
    Slot
    """

    class Meta:
        model = Slot
        fields = (
            'id',
            'day',
            'order',
            'comment',
            'config',
        )


class DayStructureSerializer(serializers.ModelSerializer):
    """
    Day serializer
    """

    slots = SlotStructureSerializer(many=True)

    class Meta:
        model = Day
        fields = (
            'id',
            'routine',
            'order',
            'name',
            'description',
            'is_rest',
            'need_logs_to_advance',
            'type',
            'config',
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
            'created',
            'start',
            'end',
            'fit_in_week',
            'days',
        )


class SlotEntrySerializer(serializers.ModelSerializer):
    """
    Slot entry serializer
    """

    # Allow omitting 'exercise' when creating a custom one
    exercise = serializers.PrimaryKeyRelatedField(queryset=Exercise.objects.all(), required=False)

    # Inline custom-creation helpers (write-only; do not persist)
    create_custom = serializers.BooleanField(write_only=True, required=False, default=False)
    custom_name = serializers.CharField(write_only=True, required=False, allow_blank=False)
    custom_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = SlotEntry
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
            'config',
            # helpers (write-only)
            'create_custom',
            'custom_name',
            'custom_notes',
        )

    def validate(self, attrs):
        has_exercise = bool(attrs.get('exercise'))
        wants_custom = bool(attrs.get('create_custom'))

        if has_exercise and wants_custom:
            raise serializers.ValidationError(
                'Provide either an existing exercise or create a custom one, not both.'
            )

        if not has_exercise and not wants_custom:
            raise serializers.ValidationError('Select a catalog exercise or add a custom one.')

        if wants_custom and not attrs.get('custom_name'):
            raise serializers.ValidationError('Custom exercise requires a name.')

        return attrs

    def _exercise_field_exists(self, field_name):
        try:
            Exercise._meta.get_field(field_name)
            return True
        except Exception:
            return False

    def _maybe_required_fk_default(self, field_name, request):
        """
        Best-effort defaults for required FKs like language/category if your Exercise model needs them.
        """
        if not self._exercise_field_exists(field_name):
            return None
        field = Exercise._meta.get_field(field_name)
        if getattr(field, 'null', False):
            return None
        Model = field.remote_field.model
        # Try a user-derived value first (if present), else first available
        candidate = None
        if request and hasattr(request, 'user'):
            # common possibilities; safe if absent
            for attr in ('language',):
                candidate = getattr(getattr(request.user, 'profile', None), attr, None)
                if isinstance(candidate, Model):
                    break
                candidate = None
        return candidate or Model.objects.first()

    # inside SlotEntrySerializer
    def _make_custom_exercise(self, name, notes):
        request = self.context.get('request')

        # fallbacks for language/category
        lang = self._maybe_required_fk_default('language', request)  # for translation
        cat = self._maybe_required_fk_default('category', request)

        # guarantee a category exists
        ExerciseCategory = apps.get_model('exercises', 'ExerciseCategory')
        if cat is None:
            cat = ExerciseCategory.objects.first() or ExerciseCategory.objects.create(name='Custom')

        # create Exercise WITHOUT 'name'
        create_kwargs = {}
        for owner_field in ('owner', 'user', 'created_by', 'creation_user'):
            if self._exercise_field_exists(owner_field) and request:
                create_kwargs[owner_field] = getattr(request, 'user', None)
        if self._exercise_field_exists('category') and cat is not None:
            create_kwargs['category'] = cat
        # only if Exercise itself has 'language' (often it doesn’t)
        if self._exercise_field_exists('language') and lang is not None:
            create_kwargs['language'] = lang

        exercise = Exercise.objects.create(**create_kwargs)

        # add translation with name/description
        ExerciseTranslation = apps.get_model('exercises', 'ExerciseTranslation')
        if ExerciseTranslation:
            tr_kwargs = {'exercise': exercise}
            if hasattr(ExerciseTranslation, 'language'):
                if lang is None:
                    LangModel = ExerciseTranslation._meta.get_field('language').remote_field.model
                    lang = LangModel.objects.first()
                tr_kwargs['language'] = lang
            if hasattr(ExerciseTranslation, 'name'):
                tr_kwargs['name'] = name
            if hasattr(ExerciseTranslation, 'description'):
                tr_kwargs['description'] = notes or ''
            ExerciseTranslation.objects.create(**tr_kwargs)

        # also create a CustomExercise so it shows on /en/exercise/my/custom-exercises/
        CustomExercise = apps.get_model('exercises', 'CustomExercise')
        if CustomExercise and request and getattr(request, 'user', None):
            ce_fields = {f.name for f in CustomExercise._meta.get_fields()}
            ce_kwargs = {'user': request.user, 'name': name, 'description': notes or ''}
            if 'exercise' in ce_fields:
                ce_kwargs['exercise'] = exercise
            if 'category' in ce_fields:
                ce_kwargs['category'] = cat
            CustomExercise.objects.create(**ce_kwargs)

        return exercise

    def create(self, validated_data):
        make_custom = validated_data.pop('create_custom', False)
        custom_name = validated_data.pop('custom_name', None)
        custom_notes = validated_data.pop('custom_notes', None)  # helpers only

        if make_custom:
            exercise = self._make_custom_exercise(custom_name, notes=custom_notes)
            validated_data['exercise'] = exercise

        return super().create(validated_data)

    def update(self, instance, validated_data):
        make_custom = validated_data.pop('create_custom', False)
        custom_name = validated_data.pop('custom_name', None)
        custom_notes = validated_data.pop('custom_notes', None)

        if make_custom:
            exercise = self._make_custom_exercise(custom_name, notes=custom_notes)
            validated_data['exercise'] = exercise

        return super().update(instance, validated_data)


class SetConfigDataSerializer(serializers.Serializer):
    """
    SetConfigData serializer
    """

    slot_entry_id = serializers.IntegerField()
    exercise = serializers.IntegerField()
    sets = serializers.IntegerField()
    max_sets = serializers.IntegerField(allow_null=True)
    weight = DecimalOrIntegerField(max_digits=6, decimal_places=2)
    max_weight = DecimalOrIntegerField(max_digits=6, decimal_places=2)
    weight_unit = serializers.IntegerField(allow_null=True)
    weight_rounding = serializers.DecimalField(max_digits=4, decimal_places=2)
    repetitions = DecimalOrIntegerField(max_digits=6, decimal_places=2)
    max_repetitions = DecimalOrIntegerField(max_digits=6, decimal_places=2)
    repetitions_unit = serializers.IntegerField(allow_null=True)
    repetitions_rounding = serializers.DecimalField(max_digits=4, decimal_places=2)
    rir = DecimalOrIntegerField(max_digits=2, decimal_places=1)
    max_rir = DecimalOrIntegerField(max_digits=2, decimal_places=1)
    rpe = DecimalOrIntegerField(max_digits=2, decimal_places=1)
    rest = DecimalOrIntegerField(max_digits=6, decimal_places=2)
    max_rest = DecimalOrIntegerField(max_digits=6, decimal_places=2)
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
    day = DaySerializer()
    slots = SlotDataSerializer(many=True, source='slots_display_mode')


class WorkoutDayDataGymModeSerializer(serializers.Serializer):
    """
    WorkoutDayData serializer - gym mode
    """

    iteration = serializers.IntegerField()
    date = serializers.DateField()
    label = serializers.CharField()
    day = DaySerializer()
    slots = SlotDataSerializer(many=True, source='slots_gym_mode')


class WorkoutSessionSerializer(serializers.ModelSerializer):
    """
    Workout session serializer
    """

    class Meta:
        model = WorkoutSession
        fields = [
            'id',
            'routine',
            'day',
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
        fields = [
            'id',
            'date',
            'session',
            'routine',
            'iteration',
            'slot_entry',
            'next_log',
            'exercise',
            'repetitions_unit',
            'repetitions',
            'repetitions_target',
            'weight_unit',
            'weight',
            'weight_target',
            'rir',
            'rir_target',
            'rest',
            'rest_target',
        ]


class LogDisplaySerializer(serializers.Serializer):
    """
    Log Display Data serializer
    """

    session = WorkoutSessionSerializer()
    logs = WorkoutLogSerializer(many=True)


class LogDataSerializer(serializers.Serializer):
    """
    Log Stats Data serializer
    """

    exercises = serializers.DictField()
    muscle = serializers.DictField()
    upper_body = serializers.DecimalField(max_digits=10, decimal_places=2)
    lower_body = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)


class GroupedLogDataSerializer(serializers.Serializer):
    """
    Log Stats Data serializer
    """

    iteration = serializers.DictField(child=LogDataSerializer())
    weekly = serializers.DictField(child=LogDataSerializer())
    daily = serializers.DictField(child=LogDataSerializer())
    mesocycle = LogDataSerializer()


class LogStatsDataSerializer(serializers.Serializer):
    """
    Log Stats Data serializer
    """

    intensity = GroupedLogDataSerializer()
    sets = GroupedLogDataSerializer()
    volume = GroupedLogDataSerializer()
