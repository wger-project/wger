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
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import (
    DataError,
    IntegrityError,
    InterfaceError,
    OperationalError,
)
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
    generics,
    status,
    viewsets,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.fields import (
    BooleanField,
    CharField,
    DictField,
    JSONField,
    ListField,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

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
from wger.utils.powersync import REGISTRY as POWERSYNC_REGISTRY
from wger.version import (
    MIN_APP_VERSION,
    MIN_SERVER_VERSION,
    get_version,
)


logger = logging.getLogger(__name__)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for the user profile

    Every user has exactly one profile, so this endpoint has no list and no
    detail route: it always reads and writes the profile of the logged-in user.
    Updating it takes a PATCH since wger 2.7; up to 2.6 it took a POST.
    """

    serializer_class = UserprofileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> UserProfile:
        return self.request.user.userprofile

    # Only way to update the profile up to wger 2.6, kept for clients that talk
    # to those servers. Deprecated instead of hidden so it reaches the schema.
    @extend_schema(
        operation_id='userprofile_update_legacy',
        deprecated=True,
        summary='Update the profile of servers up to wger 2.6',
        description=(
            'Updates the profile of the logged-in user, exactly like PATCH does.\n\n'
            'Use this if your client needs to work with wger 2.6 or older, which '
            'accept only POST on this endpoint. Servers from 2.7 on accept both, '
            'so prefer PATCH in this case.'
        ),
        request=UserprofileSerializer,
        responses={200: UserprofileSerializer},
    )
    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class VerifyEmailView(APIView):
    """
    Sends a verification email to the logged-in user
    """

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name='VerifyEmailResponse',
                fields={
                    'status': CharField(required=False),
                    'result': CharField(required=False),
                    'message': CharField(),
                },
            ),
        },
    )
    def post(self, request):
        """
        Verify the user's email address

        POST only, a GET must not send out emails as a side effect
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
                required=True,
                description='The name of the django permission such as "exercises.change_muscle"',
            ),
        ],
        responses={
            200: inline_serializer(
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


@extend_schema(
    request=LanguageCheckSerializer,
    responses={
        200: inline_serializer(
            name='LanguageCheckResponse',
            fields={'result': BooleanField()},
        ),
        400: OpenApiResponse(
            description='The input could not be detected as the given language, '
            'or the language itself is unknown'
        ),
    },
)
@api_view(['POST'])
def check_language(request):
    """
    Checks the language of a string
    """
    serializer = LanguageCheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response({'result': True})


@extend_schema(
    request=None,
    responses={
        200: inline_serializer(
            name='RefreshTokenResponse',
            fields={'refresh_token': CharField()},
        ),
    },
)
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


@extend_schema(
    responses={
        200: inline_serializer(
            name='PowersyncTokenResponse',
            fields={
                'token': CharField(),
                'powersync_url': CharField(),
            },
        ),
    },
)
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


@extend_schema(
    responses={
        200: inline_serializer(
            name='PowersyncKeysResponse',
            # A JWKS document. Left as free-form objects on purpose, the exact
            # members depend on the configured key and are consumed by a JWT
            # library rather than read field by field.
            fields={'keys': ListField(child=DictField())},
        ),
    },
)
@api_view()
def get_powersync_keys(request):
    return JsonResponse({'keys': [powersync.public_jwk()]})


@extend_schema(
    # COMPONENT_SPLIT_REQUEST appends "Request" to the name, so don't repeat it
    request=inline_serializer(
        name='PowersyncUpload',
        fields={
            'table': CharField(),
            'data': JSONField(),
        },
    ),
    responses={
        # A permanent refusal stays 200 with an `error` key, because powersync
        # treats any non-2xx as "retry" and would otherwise loop forever.
        200: inline_serializer(
            name='PowersyncUploadResponse',
            fields={
                'status': CharField(required=False),
                'error': CharField(required=False),
                'details': CharField(required=False),
            },
        ),
        403: OpenApiResponse(description='The request is not authenticated'),
        500: OpenApiResponse(description='Unclassified server error, the client should retry'),
        503: OpenApiResponse(description='Transient database error, the client should retry'),
    },
)
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

    # Handlers return either `None` (processed) or an error dict for a
    # deterministic refusal (validation, FK ownership, etc). We propagate these
    # as 200 + `{error}` since powersync treats a non-2xx status as "retry", so
    # a permanent refusal must stay 200 or the client loops forever.
    #
    # The except ladder classifies transient infrastructure errors as retry (5xx)
    try:
        result = handler.dispatch(http_verb, payload=payload, user_id=user_id)

    except (OperationalError, InterfaceError):
        # Transient infrastructure error (deadlock, lock timeout, dropped
        # connection, etc.). Expected to clear on its own, so let the client
        # retry.
        logger.warning(f'Transient DB error for PowerSync table {table}, asking client to retry')
        return JsonResponse({'error': 'Temporarily unavailable'}, status=503)

    except (DjangoValidationError, DRFValidationError, IntegrityError, DataError) as e:
        # Deterministic refusal raised from save() (constraint, model clean,
        # custom create). Retry can't fix it, so reject permanently
        logger.warning(f'PowerSync {table} rejected: {e}')
        return JsonResponse({'error': 'Validation failed', 'details': str(e)}, status=200)

    except Exception as e:
        # Unexpected and unclassified. Retry rather than silently drop the write;
        # a failure that persists is a server bug, made visible by these logs.
        logger.exception(f'Error processing PowerSync data for table {table}')
        return JsonResponse({'error': str(e)}, status=500)

    if result is not None:
        return JsonResponse(result, status=200)
    return JsonResponse({'status': 'ok!'}, status=200)
