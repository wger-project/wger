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

# Standard Library

# Django
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q

# Third Party
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# wger
from wger.manager.api.consts import BASE_CONFIG_FIELDS
from wger.manager.api.filtersets import (
    BaseConfigFilterSet,
    WorkoutLogFilterSet,
)
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


def request_user_or_trainer_q(request):
    """
    Helper function to build a Q object for filtering objects by user or trainer.
    """
    trainer_identity_pk = request.session.get('trainer.identity', None)
    if trainer_identity_pk:
        return Q(user=request.user) | Q(user_id=trainer_identity_pk)
    return Q(user=request.user)


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
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Routine.objects.none()

        return Routine.objects.filter(
            request_user_or_trainer_q(request=self.request) | Q(is_public=True)
        )

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)

    @action(detail=True, url_path='date-sequence-display')
    def date_sequence_display_mode(self, request, pk):
        """
        Return the day sequence of the routine
        """
        # profiler = cProfile.Profile()
        # profiler.enable()

        cache_key = CacheKeyMapper.routine_api_date_sequence_display_key(pk)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        out = WorkoutDayDataDisplayModeSerializer(
            self.get_object().date_sequence,
            many=True,
        ).data
        cache.set(cache_key, out, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])

        # profiler.disable()
        # profiler.dump_stats("profile_results.prof")

        return Response(out)

    @action(detail=True, url_path='date-sequence-gym')
    def date_sequence_gym_mode(self, request, pk):
        """
        Return the day sequence of the routine
        """
        cache_key = CacheKeyMapper.routine_api_date_sequence_gym_key(pk)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        out = WorkoutDayDataGymModeSerializer(self.get_object().date_sequence, many=True).data
        cache.set(cache_key, out, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])

        return Response(out)

    @action(detail=True)
    def structure(self, request, pk):
        """
        Return the full object structure of the routine.
        """
        cache_key = CacheKeyMapper.routine_api_structure_key(pk)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        out = RoutineStructureSerializer(self.get_object()).data
        cache.set(cache_key, out, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])
        return Response(out)

    @action(detail=True, url_path='logs')
    def logs(self, request, pk):
        """
        Returns the logs for the routine
        """
        cache_key = CacheKeyMapper.routine_api_logs(pk)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        out = LogDisplaySerializer(self.get_object().logs_display(), many=True).data
        cache.set(cache_key, out, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])
        return Response(out)

    @action(detail=True, url_path='stats')
    def stats(self, request, pk):
        """
        Returns the logs for the routine
        """
        cache_key = CacheKeyMapper.routine_api_stats(pk)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        out = LogStatsDataSerializer(self.get_object().calculate_log_statistics()).data
        cache.set(cache_key, out, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])

        return Response(out)


class UserRoutineTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for routine template objects
    """

    serializer_class = RoutineSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('name', 'description', 'created')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Routine.objects.none()

        # If the current user is a trainer, also return their templates.
        return Routine.templates.filter(request_user_or_trainer_q(request=self.request))


class PublicRoutineTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for public routine templates objects
    """

    serializer_class = RoutineSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('name', 'description', 'created')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return Routine.public.all()


class WorkoutSessionViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for workout sessions objects
    """

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
        """
        Only allow access to appropriate objects
        """

        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return WorkoutSession.objects.none()

        return WorkoutSession.objects.filter(user=self.request.user)

    # def create(self, request, *args, **kwargs):
    #     super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Routine, 'workout')]


class WorkoutLogViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for workout log objects
    """

    serializer_class = WorkoutLogSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_class = WorkoutLogFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return WorkoutLog.objects.none()

        return WorkoutLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer: WorkoutLogSerializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Routine, 'routine'), (WorkoutSession, 'session')]


class RoutineDayViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for routine day objects
    """

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
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Day.objects.none()

        return Day.objects.filter(routine__user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Routine, 'routine')]


class SlotViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for routine slot objects
    """

    serializer_class = SlotSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'day',
        'order',
        'comment',
    )

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Slot.objects.none()

        return Slot.objects.filter(day__routine__user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Day, 'day')]


class SlotEntryViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for routine slot entry objects
    """

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
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return SlotEntry.objects.none()

        return SlotEntry.objects.filter(slot__day__routine__user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Slot, 'slot')]


class AbstractConfigViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for weight config objects
    """

    is_private = True
    ordering_fields = '__all__'
    filterset_fields = BASE_CONFIG_FIELDS

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(SlotEntry, 'slot_entry')]


class WeightConfigViewSet(AbstractConfigViewSet):
    """
    API endpoint for weight config objects
    """

    serializer_class = WeightConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return WeightConfig.objects.none()

        return WeightConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)


class MaxWeightConfigViewSet(AbstractConfigViewSet):
    """
    API endpoint for max weight config objects
    """

    serializer_class = MaxWeightConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return MaxWeightConfig.objects.none()

        return MaxWeightConfig.objects.filter(
            slot_entry__slot__day__routine__user=self.request.user
        )


class RepetitionsConfigViewSet(AbstractConfigViewSet):
    """
    API endpoint for reps config objects
    """

    serializer_class = RepetitionsConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return RepetitionsConfig.objects.none()

        return RepetitionsConfig.objects.all()


class MaxRepetitionsConfigViewSet(AbstractConfigViewSet):
    """
    API endpoint for max reps config objects
    """

    serializer_class = MaxRepetitionsConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return MaxRepetitionsConfig.objects.none()

        return MaxRepetitionsConfig.objects.all()


class SetsConfigViewSet(AbstractConfigViewSet):
    """
    API endpoint for set config objects
    """

    serializer_class = SetNrConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return SetsConfig.objects.none()

        return SetsConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)


class MaxSetsConfigViewSet(AbstractConfigViewSet):
    """
    API endpoint for max set config objects
    """

    serializer_class = MaxSetNrConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return MaxSetsConfig.objects.none()

        return MaxSetsConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)


class RestConfigViewSet(AbstractConfigViewSet):
    """
    API endpoint for set config objects
    """

    serializer_class = RestConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return RestConfig.objects.none()

        return RestConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)


class MaxRestConfigViewSet(AbstractConfigViewSet):
    """
    API endpoint for max rest config objects
    """

    serializer_class = MaxRestConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return MaxRestConfig.objects.none()

        return MaxRestConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)


class RiRConfigViewSet(AbstractConfigViewSet):
    """
    API endpoint for set config objects
    """

    serializer_class = RiRConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return RiRConfig.objects.none()

        return RiRConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)


class MaxRiRConfigViewSet(AbstractConfigViewSet):
    """
    API endpoint for set config objects
    """

    serializer_class = MaxRiRConfigSerializer
    filterset_class = BaseConfigFilterSet

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return MaxRiRConfig.objects.none()

        return MaxRiRConfig.objects.filter(slot_entry__slot__day__routine__user=self.request.user)
