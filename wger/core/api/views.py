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

# Third Party
from rest_framework import (
    status,
    viewsets
)
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# wger
from wger import get_version
from wger.core.api.permissions import AllowRegisterUser
from wger.core.api.serializers import (
    DaysOfWeekSerializer,
    LanguageSerializer,
    LicenseSerializer,
    RepetitionUnitSerializer,
    UserApiSerializer,
    UsernameSerializer,
    UserprofileSerializer,
    UserRegistrationSerializer,
    WeightUnitSerializer
)
from wger.core.models import (
    DaysOfWeek,
    Language,
    License,
    RepetitionUnit,
    UserProfile,
    WeightUnit
)
from wger.utils.api_token import create_token
from wger.utils.permissions import (
    UpdateOnlyPermission,
    WgerPermission
)


logger = logging.getLogger(__name__)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for workout objects
    """
    is_private = True
    serializer_class = UserprofileSerializer
    permission_classes = (WgerPermission, UpdateOnlyPermission)
    ordering_fields = '__all__'

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return UserProfile.objects.filter(user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(User, 'user')]

    @action(detail=True)
    def username(self, request, pk):
        """
        Return the username
        """

        user = self.get_object().user
        return Response(UsernameSerializer(user).data)


class ApplicationVersionView(viewsets.ViewSet):
    """
    Returns the application's version
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response(get_version())


class UserAPILoginView(viewsets.ViewSet):
    """
    API endpoint for api user objects
    """
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserApiSerializer
    throttle_scope = 'login'

    def get(self, request):
        return Response({'message': "You must send a 'username' and 'password' via POST"})

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        username = serializer.data["username"]
        password = serializer.data["password"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.info(f"Tried logging via API with unknown user: '{username}'")
            return Response({'detail': 'Username or password unknown'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if user.check_password(password):
            token = create_token(user)
            return Response({'token': token.key},
                            status=status.HTTP_200_OK)
        else:
            logger.info(f"User '{username}' tried logging via API with a wrong password")
            return Response({'detail': 'Username or password unknown'},
                            status=status.HTTP_401_UNAUTHORIZED)


class UserAPIRegistrationViewSet(viewsets.ViewSet):
    """
    API endpoint for api user objects
    """
    permission_classes = (AllowRegisterUser, )
    serializer_class = UserRegistrationSerializer

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        return UserProfile.objects.filter(user=self.request.user)

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = create_token(user)

        return Response({'message': 'api user successfully registered',
                         'token': token.key},
                        status=status.HTTP_201_CREATED)


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for workout objects
    """
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    ordering_fields = '__all__'
    filterset_fields = ('full_name',
                        'short_name')


class DaysOfWeekViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for workout objects
    """
    queryset = DaysOfWeek.objects.all()
    serializer_class = DaysOfWeekSerializer
    ordering_fields = '__all__'
    filterset_fields = ('day_of_week', )


class LicenseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for workout objects
    """
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    ordering_fields = '__all__'
    filterset_fields = ('full_name',
                        'short_name',
                        'url')


class RepetitionUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for repetition units objects
    """
    queryset = RepetitionUnit.objects.all()
    serializer_class = RepetitionUnitSerializer
    ordering_fields = '__all__'
    filterset_fields = ('name', )


class WeightUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for weight units objects
    """
    queryset = WeightUnit.objects.all()
    serializer_class = WeightUnitSerializer
    ordering_fields = '__all__'
    filterset_fields = ('name', )
