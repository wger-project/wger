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

# Standard Library
import json

# Django
from django.shortcuts import get_object_or_404

# Third Party
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# wger
from wger.exercises.models import ExerciseBase
from wger.manager.api.serializers import (
    DayNgSerializer,
    RoutineSerializer,
    RoutineStructureSerializer,
    ScheduleSerializer,
    ScheduleStepSerializer,
    WorkoutDayDataDisplayModeSerializer,
    WorkoutDayDataGymModeSerializer,
    WorkoutLogSerializer,
    WorkoutSerializer,
    WorkoutSessionSerializer,
    WorkoutTemplateSerializer,
)
from wger.manager.models import (
    Routine,
    Schedule,
    ScheduleStep,
    Workout,
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.viewsets import WgerOwnerObjectModelViewSet
from wger.weight.helpers import process_log_entries


class RoutineViewSet(viewsets.ModelViewSet):
    """
    API endpoint for routine objects
    """

    serializer_class = RoutineSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'name',
        'description',
        'created',
        'start',
        'end',
    )

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Routine.objects.none()

        return Routine.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)

    @action(detail=True, url_path='day-sequence')
    def day_sequence(self, request, pk):
        """
        Return the day sequence of the routine
        """
        return Response(DayNgSerializer(self.get_object().day_sequence, many=True).data)

    @action(detail=True, url_path='date-sequence-display')
    def date_sequence_display_mode(self, request, pk):
        """
        Return the day sequence of the routine
        """
        return Response(
            WorkoutDayDataDisplayModeSerializer(self.get_object().date_sequence, many=True).data
        )

    @action(detail=True, url_path='date-sequence-gym-mode')
    def date_sequence_gym_mode(self, request, pk):
        """
        Return the day sequence of the routine
        """
        return Response(
            WorkoutDayDataGymModeSerializer(self.get_object().date_sequence, many=True).data
        )

    @action(detail=True, url_path='current-day-display-mode')
    def current_day_display_mode(self, request, pk):
        """
        Return current day of the routine
        """
        return Response(WorkoutDayDataDisplayModeSerializer(self.get_object().current_day()).data)

    @action(detail=True, url_path='current-day-gym-mode')
    def current_day_gym_mode(self, request, pk):
        """
        Return current day of the routine
        """
        return Response(WorkoutDayDataGymModeSerializer(self.get_object().current_day()).data)

    @action(detail=True)
    def structure(self, request, pk):
        """
        Return full object structure of the routine.
        """
        return Response(RoutineStructureSerializer(self.get_object()).data)


class WorkoutViewSet(viewsets.ModelViewSet):
    """
    API endpoint for routine objects
    """

    serializer_class = WorkoutSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('name', 'description', 'creation_date')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Workout.objects.none()

        return Workout.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)

    @action(detail=True)
    def log_data(self, request, pk):
        """
        Returns processed log data for graphing

        Basically, these are the logs for the workout and for a specific exercise base.

        If on a day there are several entries with the same number of repetitions,
        but different weights, only the entry with the higher weight is shown in the chart
        """
        base_id = request.GET.get('id')
        if not base_id:
            return Response("Please provide an base ID in the 'id' GET parameter")

        base = get_object_or_404(ExerciseBase, pk=base_id)
        logs = base.workoutlog_set.filter(
            user=self.request.user,
            weight_unit__in=(1, 2),
            repetition_unit=1,
            workout=self.get_object(),
        )
        entry_logs, chart_data = process_log_entries(logs)
        serialized_logs = {}
        for key, values in entry_logs.items():
            serialized_logs[str(key)] = [WorkoutLogSerializer(entry).data for entry in values]
        return Response({'chart_data': json.loads(chart_data), 'logs': serialized_logs})


class UserWorkoutTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for routine template objects
    """

    serializer_class = WorkoutTemplateSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('name', 'description', 'creation_date')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Workout.objects.none()

        return Workout.templates.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)


class PublicWorkoutTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for public workout templates objects
    """

    serializer_class = WorkoutSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('name', 'description', 'creation_date')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return Workout.templates.filter(is_public=True)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)


class WorkoutSessionViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for workout sessions objects
    """

    serializer_class = WorkoutSessionSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'date',
        'workout',
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

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Workout, 'workout')]


class ScheduleStepViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for schedule step objects
    """

    serializer_class = ScheduleStepSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'schedule',
        'workout',
        'duration',
        'order',
    )

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return ScheduleStep.objects.none()

        return ScheduleStep.objects.filter(schedule__user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Workout, 'workout'), (Schedule, 'schedule')]


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for schedule objects
    """

    serializer_class = ScheduleSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'is_active',
        'is_loop',
        'start_date',
        'name',
    )

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Schedule.objects.none()

        return Schedule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)


class WorkoutLogViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for workout log objects
    """

    serializer_class = WorkoutLogSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'date',
        'exercise_base',
        'reps',
        'weight',
        'workout',
        'repetition_unit',
        'weight_unit',
    )

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return WorkoutLog.objects.none()

        return WorkoutLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Workout, 'workout')]
