# Django / DRF
from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

# wger
from wger.manager.api.consts import BASE_CONFIG_FIELDS
from wger.manager.api.filtersets import BaseConfigFilterSet, WorkoutLogFilterSet
from wger.manager.api.permissions import RoutinePermission
from wger.manager.api.serializers import (
    DaySerializer,
    LogDisplaySerializer,
    LogStatsDataSerializer,
    MaxRepetitionsConfigSerializer,
    MaxRestConfigSerializer,
    MaxRiRConfigSerializer,
    MaxSetNrConfigSerializer,
    MaxWeightConfigSerializer,
    RepetitionsConfigSerializer,
    RestConfigSerializer,
    RiRConfigSerializer,
    RoutineSerializer,
    RoutineStructureSerializer,
    SetNrConfigSerializer,
    SlotEntrySerializer,
    SlotSerializer,
    WeightConfigSerializer,
    WorkoutDayDataDisplayModeSerializer,
    WorkoutDayDataGymModeSerializer,
    WorkoutLogSerializer,
    WorkoutSessionSerializer,
)
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
from wger.utils.cache import CacheKeyMapper
from wger.utils.viewsets import WgerOwnerObjectModelViewSet

# Try to use the real helper; if not available, fall back to current-user filter
try:
    from wger.manager.views import request_user_or_trainer_q  # noqa: F401
except Exception:
    def request_user_or_trainer_q(request):
        return Q(user=getattr(request, 'user', None))

def _safe_field_choices(model, field_name, defaults):
    """
    Try field.choices; if missing, derive from DB distinct values; else use defaults.
    Returns list of (id, name) pairs.
    """
    try:
        field = model._meta.get_field(field_name)
    except Exception:
        field = None

    if field is not None:
        choices = getattr(field, 'choices', None)
        if choices:
            return [(key, str(label)) for key, label in choices]

    # Fallback: infer from DB values
    try:
        vals = (
            model.objects.exclude(**{f"{field_name}__isnull": True})
            .values_list(field_name, flat=True)
            .distinct()
        )
        vals = [v for v in vals if v not in (None, "")]
        if vals:
            return [(v, str(v)) for v in vals]
    except Exception:
        pass

    return defaults

class MyCustomExerciseSearchView(APIView):
    """
    Devbridge-autocomplete suggestions limited to the current user's CustomExercise.
    Returns {"query": "...", "suggestions": [{"value": <name>, "data": <exercise_id>}, ...]}
    """
    def post(self, request, *args, **kwargs):
        query = (request.POST.get('query') or '').strip()
        user = request.user
        CustomExercise = apps.get_model('exercises', 'CustomExercise')
        ExerciseTranslation = apps.get_model('exercises', 'ExerciseTranslation')
        qs = CustomExercise.objects.filter(user=user)
        if query:
            qs = qs.filter(name__icontains=query)

        suggestions = []
        for ce in qs.order_by('name')[:20]:
            exercise_id = None
            # Prefer direct FK if present
            if any(f.name == 'exercise' for f in CustomExercise._meta.get_fields()):
                exercise_id = getattr(ce, 'exercise_id', None)
            # Otherwise resolve via ExerciseTranslation
            if not exercise_id:
                tr = ExerciseTranslation.objects.filter(name__iexact=ce.name).first()
                if tr:
                    exercise_id = tr.exercise_id
            if exercise_id:
                suggestions.append({'value': ce.name, 'data': exercise_id})
        return Response({'query': query, 'suggestions': suggestions})

class SettingRepetitionUnitView(APIView):
    """
    Returns available repetition units.
    GET -> [{"id": "...", "name": "..."}, ...]
    """
    def get(self, request, *args, **kwargs):
        defaults = [('reps', 'Repetitions'), ('seconds', 'Seconds')]
        pairs = _safe_field_choices(SlotEntry, 'repetition_unit', defaults)
        data = [{'id': key, 'name': name} for key, name in pairs]
        return Response(data)

class SettingWeightUnitView(APIView):
    """
    Returns available weight units.
    GET -> [{"id": "...", "name": "..."}, ...]
    """
    def get(self, request, *args, **kwargs):
        defaults = [('kg', 'Kilograms'), ('lb', 'Pounds')]
        pairs = _safe_field_choices(SlotEntry, 'weight_unit', defaults)
        data = [{'id': key, 'name': name} for key, name in pairs]
        return Response(data)

class RoutineViewSet(viewsets.ModelViewSet):
    """
    API endpoint for routine objects
    """
    serializer_class = RoutineSerializer
    permission_classes = [RoutinePermission]
    ordering_fields = '__all__'
    filterset_fields = (
        'name',
        'description',
        'created',
        'start',
        'end',
        'is_public',
        'is_template',
    )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Routine.objects.none()
        return Routine.objects.filter(
            request_user_or_trainer_q(request=self.request) | Q(is_public=True)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, url_path='date-sequence-display')
    def date_sequence_display_mode(self, request, pk):
        cache_key = CacheKeyMapper.routine_api_date_sequence_display_key(pk)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        out = WorkoutDayDataDisplayModeSerializer(self.get_object().date_sequence, many=True).data
        cache.set(cache_key, out, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])
        return Response(out)

    @action(detail=True, url_path='date-sequence-gym')
    def date_sequence_gym_mode(self, request, pk):
        cache_key = CacheKeyMapper.routine_api_date_sequence_gym_key(pk)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        out = WorkoutDayDataGymModeSerializer(self.get_object().date_sequence, many=True).data
        cache.set(cache_key, out, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])
        return Response(out)

    @action(detail=True)
    def structure(self, request, pk):
        cache_key = CacheKeyMapper.routine_api_structure_key(pk)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        out = RoutineStructureSerializer(self.get_object()).data
        cache.set(cache_key, out, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])
        return Response(out)

    @action(detail=True, url_path='logs')
    def logs(self, request, pk):
        cache_key = CacheKeyMapper.routine_api_logs(pk)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        out = LogDisplaySerializer(self.get_object().logs_display(), many=True).data
        cache.set(cache_key, out, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])
        return Response(out)

    @action(detail=True, url_path='stats')
    def stats(self, request, pk):
        cache_key = CacheKeyMapper.routine_api_stats(pk)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        out = LogStatsDataSerializer(self.get_object().calculate_log_statistics()).data
        cache.set(cache_key, out, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])
        return Response(out)

class UserRoutineTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoutineSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('name', 'description', 'created')

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Routine.objects.none()
        return Routine.templates.filter(request_user_or_trainer_q(request=self.request))

class PublicRoutineTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoutineSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('name', 'description', 'created')

    def get_queryset(self):
        return Routine.public.all()

class WorkoutSessionViewSet(WgerOwnerObjectModelViewSet):
    serializer_class = WorkoutSessionSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'date',
        'routine',
        'notes',
        'impression',
        'time_start',
        'time_end',
    )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WorkoutSession.objects.none()
        return WorkoutSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_owner_objects(self):
        return [(Routine, 'workout')]

class WorkoutLogViewSet(WgerOwnerObjectModelViewSet):
    serializer_class = WorkoutLogSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_class = WorkoutLogFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WorkoutLog.objects.none()
        return WorkoutLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer: WorkoutLogSerializer):
        serializer.save(user=self.request.user)

    def get_owner_objects(self):
        return [(Routine, 'routine'), (WorkoutSession, 'session')]

class RoutineDayViewSet(WgerOwnerObjectModelViewSet):
    serializer_class = DaySerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'id',
        'order',
        'name',
        'description',
        'is_rest',
        'need_logs_to_advance',
    )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Day.objects.none()
        return Day.objects.filter(routine__user=self.request.user)

    def get_owner_objects(self):
        return [(Routine, 'routine')]

class SlotViewSet(WgerOwnerObjectModelViewSet):
    serializer_class = SlotSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'day',
        'order',
        'comment',
    )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Slot.objects.none()
        return Slot.objects.filter(day__routine__user=self.request.user)

    def get_owner_objects(self):
        return [(Day, 'day')]

class SlotEntryViewSet(WgerOwnerObjectModelViewSet):
    serializer_class = SlotEntrySerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'slot',
        'exercise',
        'type',
        'repetition_unit',
        'repetition_rounding',
        'weight_unit',
        'weight_rounding',
        'order',
        'comment',
    )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SlotEntry.objects.none()
        return SlotEntry.objects.filter(slot__day__routine__user=self.request.user)

    def get_owner_objects(self):
        return [(Slot, 'slot')]

class AbstractConfigViewSet(WgerOwnerObjectModelViewSet):
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = BASE_CONFIG_FIELDS

    def get_owner_objects(self):
        return [(SlotEntry, 'slot_entry')]

class WeightConfigViewSet(AbstractConfigViewSet):
    serializer_class = WeightConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WeightConfig.objects.none()
        return WeightConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)

class MaxWeightConfigViewSet(AbstractConfigViewSet):
    serializer_class = MaxWeightConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MaxWeightConfig.objects.none()
        return MaxWeightConfig.objects.filter(
            slot_entry__slot__day__routine__user=self.request.user
        )

class RepetitionsConfigViewSet(AbstractConfigViewSet):
    serializer_class = RepetitionsConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return RepetitionsConfig.objects.none()
        return RepetitionsConfig.objects.all()

class MaxRepetitionsConfigViewSet(AbstractConfigViewSet):
    serializer_class = MaxRepetitionsConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MaxRepetitionsConfig.objects.none()
        return MaxRepetitionsConfig.objects.all()

class SetsConfigViewSet(AbstractConfigViewSet):
    serializer_class = SetNrConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SetsConfig.objects.none()
        return SetsConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)

class MaxSetsConfigViewSet(AbstractConfigViewSet):
    serializer_class = MaxSetNrConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MaxSetsConfig.objects.none()
        return MaxSetsConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)

class RestConfigViewSet(AbstractConfigViewSet):
    serializer_class = RestConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return RestConfig.objects.none()
        return RestConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)

class MaxRestConfigViewSet(AbstractConfigViewSet):
    serializer_class = MaxRestConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MaxRestConfig.objects.none()
        return MaxRestConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)

class RiRConfigViewSet(AbstractConfigViewSet):
    serializer_class = RiRConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return RiRConfig.objects.none()
        return RiRConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)

class MaxRiRConfigViewSet(AbstractConfigViewSet):
    serializer_class = MaxRiRConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MaxRiRConfig.objects.none()
        return MaxRiRConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)
