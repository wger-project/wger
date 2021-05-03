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

# Django
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

# Third Party
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# wger
from wger.core.models import (
    DaysOfWeek,
    Language,
    License,
    RepetitionUnit,
    UserProfile,
    WeightUnit
)


class UserprofileSerializer(serializers.ModelSerializer):
    """
    Workout session serializer
    """
    class Meta:
        model = UserProfile
        fields = ['user',
                  'gym',
                  'is_temporary',
                  'show_comments',
                  'show_english_ingredients',
                  'workout_reminder_active',
                  'workout_reminder',
                  'workout_duration',
                  'last_workout_notification',
                  'notification_language',
                  'timer_active',
                  'timer_active',
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
                  'num_days_weight_reminder']


class UsernameSerializer(serializers.Serializer):
    """
    Serializer to extract the username
    """
    username = serializers.CharField()


class UserApiSerializer(serializers.ModelSerializer):
    """ Serializer to map to User model in relation to api user"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password']


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(required=True,
                                     validators=[UniqueValidator(queryset=User.objects.all())])
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
        fields = ['short_name',
                  'full_name']


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
        fields = ['id',
                  'full_name',
                  'short_name',
                  'url']


class RepetitionUnitSerializer(serializers.ModelSerializer):
    """
    Repetition unit serializer
    """
    class Meta:
        model = RepetitionUnit
        fields = ['id',
                  'name']


class WeightUnitSerializer(serializers.ModelSerializer):
    """
    Weight unit serializer
    """
    class Meta:
        model = WeightUnit
        fields = ['id', 'name']
