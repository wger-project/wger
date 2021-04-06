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
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404

# Third Party
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# wger
from wger.exercises.models import Exercise
from wger.manager.api.serializers import (
    DaySerializer,
    ScheduleSerializer,
    ScheduleStepSerializer,
    SetSerializer,
    SettingSerializer,
    WorkoutCanonicalFormSerializer,
    WorkoutLogSerializer,
    WorkoutSerializer,
    WorkoutSessionSerializer
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
from wger.utils.viewsets import WgerOwnerObjectModelViewSet
from wger.weight.helpers import process_log_entries


class WorkoutViewSet(viewsets.ModelViewSet):
    """
    API endpoint for workout objects
    """
    serializer_class = WorkoutSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('comment',
                        'creation_date')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return Workout.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)

    @action(detail=True)
    def canonical_representation(self, request, pk):
        """
        Output the canonical representation of a workout

        This is basically the same form as used in the application
        """

        out = WorkoutCanonicalFormSerializer(self.get_object().canonical_representation).data
        return Response(out)

    @action(detail=True)
    def log_data(self, request, pk):
        """
        Returns processed log data for graphing

        Basically, these are the logs for the workout and for a specific exercise.

        If on a day there are several entries with the same number of repetitions,
        but different weights, only the entry with the higher weight is shown in the chart
        """
        execise_id = request.GET.get('id')
        if not execise_id:
            return Response("Please provide an exercise ID in the 'id' GET parameter")

        exercise = get_object_or_404(Exercise, pk=execise_id)
        logs = exercise.workoutlog_set.filter(user=self.request.user,
                                              weight_unit__in=(1, 2),
                                              repetition_unit=1,
                                              workout=self.get_object())
        entry_logs, chart_data = process_log_entries(logs)
        serialized_logs = {}
        for key, values in entry_logs.items():
            serialized_logs[str(key)] = [WorkoutLogSerializer(entry).data for entry in values]
        return Response({'chart_data': json.loads(chart_data), 'logs': serialized_logs})


class WorkoutSessionViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for workout sessions objects
    """
    serializer_class = WorkoutSessionSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('date',
                        'workout',
                        'notes',
                        'impression',
                        'time_start',
                        'time_end')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
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
    filterset_fields = ('schedule',
                        'workout',
                        'duration',
                        'order')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return ScheduleStep.objects.filter(schedule__user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Workout, 'workout'),
                (Schedule, 'schedule')]


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for schedule objects
    """
    serializer_class = ScheduleSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('is_active',
                        'is_loop',
                        'start_date',
                        'name')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return Schedule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)


class DayViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for training day objects
    """
    serializer_class = DaySerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('description',
                        'training',
                        'day')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return Day.objects.filter(training__user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Workout, 'training')]


class SetViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for workout set objects
    """
    serializer_class = SetSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('exerciseday',
                        'order',
                        'sets')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return Set.objects.filter(exerciseday__training__user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Day, 'exerciseday')]

    @action(detail=True)
    def computed_settings(self, request, pk):
        """Returns the synthetic settings for this set"""

        out = SettingSerializer(self.get_object().compute_settings, many=True).data
        return Response({'results': out})

    @action(detail=True)
    def smart_text(self, request, pk):
        """Returns the smart text representation for the reps"""

        try:
            exercise = get_object_or_404(Exercise, pk=int(self.request.GET.get('exercise')))
        except ValueError:
            return HttpResponseNotFound()
        return Response({'results': self.get_object().reps_smart_text(exercise=exercise)})


class SettingViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for repetition setting objects
    """
    serializer_class = SettingSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('exercise',
                        'order',
                        'reps',
                        'weight',
                        'set',
                        'order')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return Setting.objects.filter(set__exerciseday__training__user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the order
        """
        serializer.save(order=1)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Set, 'set')]


class WorkoutLogViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for workout log objects
    """
    serializer_class = WorkoutLogSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('date',
                        'exercise',
                        'reps',
                        'weight',
                        'workout')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """

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
