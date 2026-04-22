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
from allauth.account.models import EmailAddress
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
from rest_framework.fields import (
    BooleanField,
    CharField,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

# wger
import wger.manager.powersync as ps_manager
import wger.measurements.powersync as ps_measurements
import wger.weight.powersync as ps_weight
from wger.core.api import powersync
from wger.core.api.serializers import (
    LanguageCheckSerializer,
    LanguageSerializer,
    LicenseSerializer,
    RepetitionUnitSerializer,
    RoutineWeightUnitSerializer,
    UserLoginSerializer,
    UserprofileSerializer,
    UserRegistrationSerializer,
)
from wger.core.forms import UserLoginForm
from wger.core.models import (
    Language,
    License,
    RepetitionUnit,
    UserProfile,
    WeightUnit,
)
from wger.utils.api_token import create_token
from wger.utils.permissions import WgerPermission
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
        data = request.data
        serializer = self.serializer_class(request.user.userprofile, data=data)
        if serializer.is_valid():
            serializer.save()

            # New email, update the user and reset the email verification flag
            if data.get('email') and request.user.email != data['email']:
                request.user.email = data['email']
                request.user.save()
                request.user.userprofile.save()
                # adds new email if it is not already registered
                EmailAddress.objects.add_email(
                    request,
                    request.user,
                    request.user.email,
                    confirm=True,
                )
                logger.debug('adding new email with verified flag , send verification email')

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


class UserAPILoginView(viewsets.ViewSet):
    """
    API login endpoint. Returns a token that can subsequently passed in the
    header.

    Note that it is recommended to use token authorization instead.
    """

    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer
    throttle_scope = 'login'

    def get(self, request):
        return Response(data={'message': "You must send a 'username' and 'password' via POST"})

    @extend_schema(
        parameters=[],
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='loginSerializer',
                fields={'token': CharField()},
            ),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data, request=request)
        serializer.is_valid(raise_exception=True)

        # This is a bit hacky, but saving the email or username as the username
        # allows us to simply use the helpers.EmailAuthBackend backend which also
        # uses emails
        username = serializer.data.get('username', serializer.data.get('email', None))
        data = {'username': username, 'password': serializer.data['password']}
        form = UserLoginForm(data=data, authenticate_on_clean=False)

        if not form.is_valid():
            logger.info(f"Tried logging via API with unknown user : '{username}'")
            return Response(
                {'detail': 'Username or password unknown'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        form.authenticate(request)
        token = create_token(form.get_user())
        return Response(
            data={'token': token.key},
            status=status.HTTP_200_OK,
            headers={
                'Deprecation': 'Sat, 01 Oct 2022 23:59:59 GMT',
            },
        )


class UserAPIRegistrationViewSet(viewsets.ViewSet):
    """
    API endpoint
    """

    # permission_classes = (AllowRegisterUser,)
    serializer_class = UserRegistrationSerializer
    throttle_scope = 'registration'

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return UserProfile.objects.filter(user=self.request.user)

    @extend_schema(
        parameters=[],
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='loginSerializer',
                fields={'token': CharField()},
            ),
        },
    )
    def post(self, request):
        if not settings.WGER_SETTINGS['ALLOW_REGISTRATION']:
            return Response(
                {'message': 'Registration is not allowed on this instance'},
                status=status.HTTP_200_OK,
            )

        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # user.userprofile.added_by = request.user
        user.userprofile.save()
        token = create_token(user)

        EmailAddress.objects.add_email(request, user, user.email, confirm=True)

        return Response(
            {'message': 'api user successfully registered', 'token': token.key},
            status=status.HTTP_201_CREATED,
        )


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

    try:
        match table:
            # Body weight
            case 'weight_weightentry':
                if http_verb == 'PUT':
                    ps_weight.handle_create(payload=payload, user_id=user_id, request=request)
                elif http_verb == 'PATCH':
                    ps_weight.handle_update(payload=payload, user_id=user_id, request=request)
                elif http_verb == 'DELETE':
                    ps_weight.handle_delete(payload=payload, user_id=user_id)

            # Measurements
            case 'measurements_category':
                if http_verb == 'PUT':
                    ps_measurements.handle_create_category(payload=payload, user_id=user_id)
                elif http_verb == 'PATCH':
                    ps_measurements.handle_update_category(payload=payload, user_id=user_id)
                elif http_verb == 'DELETE':
                    ps_measurements.handle_delete_category(payload=payload, user_id=user_id)

            case 'measurements_measurement':
                if http_verb == 'PUT':
                    ps_measurements.handle_create_measurement(payload=payload, user_id=user_id)
                elif http_verb == 'PATCH':
                    ps_measurements.handle_update_measurement(payload=payload, user_id=user_id)
                elif http_verb == 'DELETE':
                    ps_measurements.handle_delete_measurement(payload=payload, user_id=user_id)

            # Routines
            case 'manager_workoutlog':
                if http_verb == 'PUT':
                    ps_manager.handle_create_log(payload=payload, user_id=user_id)
                elif http_verb == 'PATCH':
                    ps_manager.handle_update_log(payload=payload, user_id=user_id)
                elif http_verb == 'DELETE':
                    ps_manager.handle_delete_log(payload=payload, user_id=user_id)

            case 'manager_workoutsession':
                if http_verb == 'PUT':
                    ps_manager.handle_create_session(payload=payload, user_id=user_id)
                elif http_verb == 'PATCH':
                    ps_manager.handle_update_session(payload=payload, user_id=user_id)
                elif http_verb == 'DELETE':
                    ps_manager.handle_delete_session(payload=payload, user_id=user_id)

            case _:
                logger.warning(f'Received unknown PowerSync table: {table}')
                return JsonResponse({'error': f'Unknown table: {table}'}, status=200)
    except Exception as e:
        logger.exception(f'Error processing PowerSync data for table {table}')
        return JsonResponse({'error': str(e)}, status=200)

    return JsonResponse({'status': 'ok!'}, status=200)
