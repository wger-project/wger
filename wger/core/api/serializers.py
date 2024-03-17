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
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.http import HttpRequest

# Third Party
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.validators import UniqueValidator

# wger
from wger.core.models import (
    DaysOfWeek,
    Language,
    License,
    RepetitionUnit,
    UserProfile,
    WeightUnit,
)


logger = logging.getLogger(__name__)


class UserprofileSerializer(serializers.ModelSerializer):
    """
    Workout session serializer
    """

    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.EmailField(source='user.username', read_only=True)
    date_joined = serializers.EmailField(source='user.date_joined', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'username',
            'email',
            'email_verified',
            'is_trustworthy',
            'date_joined',
            'gym',
            'is_temporary',
            'show_comments',
            'show_english_ingredients',
            'workout_reminder_active',
            'workout_reminder',
            'workout_duration',
            'last_workout_notification',
            'notification_language',
            'age',
            'birthdate',
            'height',
            'gender',
            'sleep_hours',
            'work_hours',
            'work_intensity',
            'sport_hours',
            'sport_intensity',
            'freetime_hours',
            'freetime_intensity',
            'calories',
            'weight_unit',
            'ro_access',
            'num_days_weight_reminder',
        ]


class UserLoginSerializer(serializers.ModelSerializer):
    """Serializer to map to User model in relation to api user"""

    email = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=True, min_length=8)

    request: HttpRequest

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def __init__(self, request: HttpRequest = None, instance=None, data=empty, **kwargs):
        self.request = request
        super().__init__(instance, data, **kwargs)

    def validate(self, data):
        email = data.get('email', None)
        username = data.get('username', None)
        password = data.get('password', None)

        if email is None and username is None:
            raise serializers.ValidationError('Please provide an "email" or a "username"')

        user_username = authenticate(request=self.request, username=username, password=password)
        user_email = authenticate(request=self.request, username=email, password=password)
        user = user_username or user_email

        if user is None:
            logger.info(f"Tried logging via API with unknown user: '{username}'")
            raise serializers.ValidationError('Username or password unknown')

        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ],
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'])
        user.set_password(validated_data['password'])
        if validated_data.get('email'):
            user.email = validated_data['email']
        user.save()

        return user


class LanguageSerializer(serializers.ModelSerializer):
    """
    Language serializer
    """

    class Meta:
        model = Language
        fields = [
            'id',
            'short_name',
            'full_name',
            'full_name_en',
        ]


class DaysOfWeekSerializer(serializers.ModelSerializer):
    """
    DaysOfWeek serializer
    """

    class Meta:
        model = DaysOfWeek
        fields = ['day_of_week']


class LicenseSerializer(serializers.ModelSerializer):
    """
    License serializer
    """

    class Meta:
        model = License
        fields = [
            'id',
            'full_name',
            'short_name',
            'url',
        ]


class RepetitionUnitSerializer(serializers.ModelSerializer):
    """
    Repetition unit serializer
    """

    class Meta:
        model = RepetitionUnit
        fields = ['id', 'name']


class RoutineWeightUnitSerializer(serializers.ModelSerializer):
    """
    Weight unit serializer
    """

    class Meta:
        model = WeightUnit
        fields = ['id', 'name']
