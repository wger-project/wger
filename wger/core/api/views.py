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
from django.conf import settings
from django.contrib.auth.models import User
from django.http import (
    HttpResponseForbidden,
    JsonResponse,
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Third Party
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import (
    action,
    api_view,
    permission_classes,
)
from rest_framework.fields import BooleanField
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

# wger
# The per-app powersync modules are imported for their side effect: each one
# registers its handlers with wger.utils.powersync.REGISTRY at import time.
import wger.core.powersync  # noqa: F401
import wger.gallery.powersync  # noqa: F401
import wger.manager.powersync  # noqa: F401
import wger.measurements.powersync  # noqa: F401
import wger.nutrition.powersync  # noqa: F401
import wger.weight.powersync  # noqa: F401
from wger.core.api import powersync
from wger.core.api.serializers import (
    LanguageCheckSerializer,
    LanguageSerializer,
    LicenseSerializer,
    RepetitionUnitSerializer,
    RoutineWeightUnitSerializer,
    UserprofileSerializer,
)
from wger.core.models import (
    Language,
    License,
    RepetitionUnit,
    UserProfile,
    WeightUnit,
)
from wger.utils.headless_long_lived import mint_long_lived_refresh_token
from wger.utils.permissions import WgerPermission
from wger.utils.powersync import REGISTRY as POWERSYNC_REGISTRY
from wger.version import (
    MIN_APP_VERSION,
    MIN_SERVER_VERSION,
    get_version,
)


logger = logging.getLogger(__name__)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for the user profile

    This endpoint works somewhat differently than the others since it always
    returns the data for the currently logged-in user's profile. To update
    the profile, use a POST request with the new data, not a PATCH.
    """

    serializer_class = UserprofileSerializer
    permission_classes = (
        IsAuthenticated,
        WgerPermission,
    )

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, 'swagger_fake_view', False):
            return UserProfile.objects.none()

        return UserProfile.objects.filter(user=self.request.user)

    @staticmethod
    def get_owner_objects():
        """
        Return objects to check for ownership permission
        """
        return [(User, 'user')]

    def list(self, request, *args, **kwargs):
        """
        Customized list view, that returns only the current user's data
        """
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset.first(), many=False)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.userprofile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, url_name='verify-email', url_path='verify-email')
    def verify_email(self, request):
        """
        Verify the user's email address
        """
        email_obj = request.user.userprofile.get_allauth_email

        if email_obj is None:
            return Response({'result': 'not sent', 'message': 'The user has no associated email'})

        if email_obj.verified:
            return Response({'status': 'verified', 'message': 'This email is already verified'})

        email_obj.send_confirmation(request)
        return Response(
            {'status': 'sent', 'message': f'A verification email was sent to {request.user.email}'}
        )


class ApplicationVersionView(viewsets.ViewSet):
    """
    Returns the application's version
    """

    permission_classes = (AllowAny,)

    @staticmethod
    @extend_schema(
        parameters=[],
        responses={
            200: OpenApiTypes.STR,
        },
    )
    def get(request):
        return Response(get_version())


class PermissionView(viewsets.ViewSet):
    """
    Checks whether the user has a django permission
    """

    permission_classes = (AllowAny,)

    @staticmethod
    @extend_schema(
        parameters=[
            OpenApiParameter(
                'permission',
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description='The name of the django permission such as "exercises.change_muscle"',
            ),
        ],
        responses={
            201: inline_serializer(
                name='PermissionResponse',
                fields={
                    'result': BooleanField(),
                },
            ),
            400: OpenApiResponse(
                description="Please pass a permission name in the 'permission' parameter"
            ),
        },
    )
    def get(request):
        permission = request.query_params.get('permission')

        if permission is None:
            return Response(
                "Please pass a permission name in the 'permission' parameter",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.is_anonymous:
            return Response({'result': False})

        return Response({'result': request.user.has_perm(permission)})


class RequiredApplicationVersionView(viewsets.ViewSet):
    """
    Returns the minimum required version of flutter app to access this server.
    """

    permission_classes = (AllowAny,)

    @staticmethod
    @extend_schema(
        parameters=[],
        responses={
            200: OpenApiTypes.STR,
        },
    )
    def get(request):
        return Response(str(MIN_APP_VERSION))


class RequiredServerVersionView(viewsets.ViewSet):
    """
    Returns the minimum required version of the server to perform sync requests
    """

    permission_classes = (AllowAny,)

    @staticmethod
    @extend_schema(
        parameters=[],
        responses={
            200: OpenApiTypes.STR,
        },
    )
    def get(request):
        return Response(str(MIN_SERVER_VERSION))


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for the languages used in the application
    """

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    ordering_fields = '__all__'
    filterset_fields = ('full_name', 'short_name')

    @method_decorator(cache_page(settings.WGER_SETTINGS['EXERCISE_CACHE_TTL']))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class LicenseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for license objects
    """

    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    ordering_fields = '__all__'
    filterset_fields = (
        'full_name',
        'short_name',
        'url',
    )


class RepetitionUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for repetition units objects
    """

    queryset = RepetitionUnit.objects.all()
    serializer_class = RepetitionUnitSerializer
    ordering_fields = '__all__'
    filterset_fields = ('name',)


class RoutineWeightUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for weight units objects
    """

    queryset = WeightUnit.objects.all()
    serializer_class = RoutineWeightUnitSerializer
    ordering_fields = '__all__'
    filterset_fields = ('name',)


@api_view(['POST'])
def check_language(request):
    """
    Checks the language of a string
    """
    serializer = LanguageCheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response({'result': True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issue_refresh_token(request):
    """
    Temporary endpoint for issuing refresh tokens for authenticated users.

    This endpoint is used to allow users of the mobile app to seamlessly move from
    permanent tokens to JWT ones.

    TODO: remove one version after the iniial offline-mode release
    """
    refresh_token = mint_long_lived_refresh_token(
        request.user,
        settings.HEADLESS_JWT_REFRESH_TOKEN_EXPIRES_IN,
    )
    return Response({'refresh_token': refresh_token})


@api_view()
@permission_classes([IsAuthenticated])
def get_powersync_token(request):

    url = (
        f'{settings.SITE_URL}/{settings.POWERSYNC_URL_PATH.strip("/")}/'
        if not settings.POWERSYNC_URL
        else settings.POWERSYNC_URL
    )

    return JsonResponse(
        {
            'token': powersync.create_token(request.user.id),
            'powersync_url': url,
        }
    )


@api_view()
def get_powersync_keys(request):
    return JsonResponse({'keys': [powersync.public_jwk()]})


@api_view(['PUT', 'PATCH', 'DELETE'])
def upload_powersync_data(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    user_id = request.user.id
    data = request.data
    http_verb = request.method

    try:
        table = data['table']
        payload = data['data']
    except (KeyError, TypeError):
        return JsonResponse(
            {'error': 'Missing required fields: table, data'},
            status=200,
        )

    logger.info(f'Received PowerSync data for table {table} via {http_verb} for user {user_id}')

    handler = POWERSYNC_REGISTRY.get(table)
    if handler is None:
        logger.warning(f'Received unknown PowerSync table: {table}')
        return JsonResponse({'error': f'Unknown table: {table}'}, status=200)

    # Handlers return either `None` (operation processed successfully) or an
    # error dict which we propagate back to the client. The HTTP status stays
    # at 200 even on logical errors, since powersync treats non-2xx statuses
    # as "retry forever".
    try:
        result = handler.dispatch(http_verb, payload=payload, user_id=user_id)
    except Exception as e:
        logger.exception(f'Error processing PowerSync data for table {table}')
        return JsonResponse({'error': str(e)}, status=200)

    if result is not None:
        return JsonResponse(result, status=200)
    return JsonResponse({'status': 'ok!'}, status=200)
