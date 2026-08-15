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
import logging

# Django
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

# Third Party
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# wger
from wger.measurements.api.aggregates import (
    DEFAULT_MAX_POINTS,
    InvalidBucket,
    bucket_rows,
    parse_timezone,
    value_count_rows,
)
from wger.measurements.api.filtersets import MeasurementEntryFilterSet
from wger.measurements import dynamic
from wger.measurements.api.serializers import (
    BucketSerializer,
    CategorySerializer,
    DynamicTypeSerializer,
    MeasurementSerializer,
    ValueCountSerializer,
)
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.utils.viewsets import WgerOwnerObjectModelViewSet


logger = logging.getLogger(__name__)


class CategoryViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for measurement units
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = ('id', 'name', 'unit', 'metric_type', 'parent', 'is_official')

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Category.objects.none()

        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """
        Official categories hold the data of the legacy weight endpoint and
        must not be deleted
        """
        if instance.is_official:
            raise PermissionDenied('Official categories cannot be deleted')
        instance.delete()

    @staticmethod
    def get_owner_objects():
        """
        Return objects to check for ownership permission
        """
        return [(User, 'user'), (Category, 'parent')]

    @extend_schema(
        summary='Read the available calculated category types',
        responses={200: DynamicTypeSerializer(many=True)},
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='dynamic-types',
        serializer_class=DynamicTypeSerializer,
    )
    def dynamic_types(self, request):
        """
        The calculated types a category can be switched to, with the schema
        their dynamic_params have to match
        """
        rows = [
            {'value': calc.slug, 'label': calc.label, 'params_schema': calc.params_schema}
            for calc in dynamic.all_types()
        ]
        return Response(DynamicTypeSerializer(rows, many=True).data)


class MeasurementViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for measurements
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MeasurementSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_class = MeasurementEntryFilterSet

    @staticmethod
    def get_owner_objects():
        """
        Return objects to check for ownership permission
        """
        return [(Category, 'category')]

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return Measurement.objects.none()

        return Measurement.objects.filter(category__user=self.request.user)

    def perform_destroy(self, instance):
        """
        The entries of a calculated category are maintained by the server;
        deleting one would only have the next reconcile recreate it
        """
        if instance.category.dynamic_type != Category.DynamicType.NONE:
            raise PermissionDenied(
                'The entries of a calculated category are maintained by the server'
            )
        instance.delete()

    def _read_max_points(self) -> int:
        try:
            return max(1, int(self.request.query_params.get('max_points', DEFAULT_MAX_POINTS)))
        except ValueError:
            raise InvalidBucket('max_points must be a number')

    @extend_schema(
        summary='Read the entries condensed into chart points',
        parameters=[
            OpenApiParameter(
                'bucket',
                description='Calendar unit to condense into. The default picks the finest one '
                'that keeps the series under max_points.',
                enum=['auto', 'hour', 'day', 'week', 'month'],
            ),
            OpenApiParameter(
                'tz',
                description='IANA name of the zone the buckets are cut in, the server zone by '
                'default. The column is UTC, and a reading after midnight belongs to the day '
                'the user had it.',
            ),
            OpenApiParameter(
                'max_points',
                type=int,
                description=f'Points the auto bucket aims for, {DEFAULT_MAX_POINTS} by default',
            ),
        ],
        responses={200: BucketSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], serializer_class=BucketSerializer)
    def aggregate(self, request):
        """
        The entries condensed into what a chart draws: one row per category,
        calendar bucket and stored unit.

        Takes the filters of the list endpoint (`category`, `category__in`,
        `date__gte`, ...) plus `bucket` (`auto`, the default, or one of hour,
        day, week, month), `tz` and `max_points`. A separate route rather than
        a mode of the list, because a bucket is not a measurement: it has no
        id, and nothing that reads measurements should have to tell them apart.
        """
        try:
            rows = bucket_rows(
                self.filter_queryset(self.get_queryset()),
                request.query_params.get('bucket', 'auto'),
                parse_timezone(request.query_params.get('tz')),
                self._read_max_points(),
            )
        except InvalidBucket as e:
            return Response({'detail': str(e)}, status=400)

        return Response(BucketSerializer(rows, many=True).data)

    @extend_schema(
        summary='Read how often each value occurred',
        parameters=[
            OpenApiParameter('tz', description='IANA name of the zone the days are cut in'),
            OpenApiParameter(
                'summed_per_day',
                type=bool,
                description='Count daily totals rather than single readings, for the metrics '
                'whose samples mean nothing on their own (steps, sleep)',
            ),
        ],
        responses={200: ValueCountSerializer(many=True)},
    )
    @action(
        detail=False,
        url_path='value-counts',
        methods=['get'],
        serializer_class=ValueCountSerializer,
    )
    def value_counts(self, request):
        """
        How often each value occurred, which is what a histogram bins.

        Takes the same filters, plus `tz` and `summed_per_day` for the metrics
        whose samples mean nothing on their own (steps, sleep), which are
        counted as daily totals instead.
        """
        try:
            rows = value_count_rows(
                self.filter_queryset(self.get_queryset()),
                parse_timezone(request.query_params.get('tz')),
                request.query_params.get('summed_per_day') in ('1', 'true', 'True'),
            )
        except InvalidBucket as e:
            return Response({'detail': str(e)}, status=400)

        return Response(ValueCountSerializer(rows, many=True).data)
