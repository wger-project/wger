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

# Third Party
from lingua import LanguageDetectorBuilder
from rest_framework import serializers

# wger
from wger.core.models import (
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

    # Email is read-only here; the app manages email changes through
    # allauth.headless (POST /_allauth/app/v1/account/email).
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    email_verified = serializers.BooleanField(source='is_verified', read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            'username',
            'email',
            'email_verified',
            'is_trustworthy',
            'date_joined',
            'gym',
            'weight_rounding',
            'repetitions_rounding',
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
        )


class LanguageSerializer(serializers.ModelSerializer):
    """
    Language serializer
    """

    class Meta:
        model = Language
        fields = (
            'id',
            'short_name',
            'full_name',
            'full_name_en',
        )


class LicenseSerializer(serializers.ModelSerializer):
    """
    License serializer
    """

    class Meta:
        model = License
        fields = (
            'id',
            'full_name',
            'short_name',
            'url',
        )


class RepetitionUnitSerializer(serializers.ModelSerializer):
    """
    Repetition unit serializer
    """

    class Meta:
        model = RepetitionUnit
        fields = ('id', 'name', 'unit_type', 'multiplier')


class RoutineWeightUnitSerializer(serializers.ModelSerializer):
    """
    Weight unit serializer
    """

    class Meta:
        model = WeightUnit
        fields = ('id', 'name')


class LanguageCheckSerializer(serializers.Serializer):
    """
    Serializer for language check
    """

    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all(), required=False)
    language_code = serializers.CharField(required=False, min_length=2, max_length=2)
    input = serializers.CharField(min_length=10)

    def validate(self, data):
        """
        Check that the detected language of the description corresponds with the
        provided language.
        """
        language = data.get('language')
        language_code = data.get('language_code')

        if not language and not language_code:
            raise serializers.ValidationError(
                {'language': 'Either a language ID or a language code must be provided.'}
            )

        if not language:
            try:
                language = Language.objects.get(short_name=language_code)
            except Language.DoesNotExist:
                raise serializers.ValidationError(
                    {'language': f'Language with code "{language_code}" does not exist.'}
                )

        # Try to detect the language
        detector = LanguageDetectorBuilder.from_all_languages().build()
        input_str = data.get('input')

        detected_language = detector.detect_language_of(input_str)
        if detected_language is None:
            raise serializers.ValidationError(
                {
                    'check': {
                        'result': False,
                        'detected_language': None,
                        'message': 'Could not detect the language of the input. Try '
                        'adding more content or rephrasing your text, language '
                        'detection works better with longer or more complete sentences.',
                    }
                }
            )

        detected_language_code = detected_language.iso_code_639_1.name.lower()
        confidence_values = detector.compute_language_confidence_values(input_str)
        logger.debug(
            f'Detected language: {detected_language_code}, '
            f'confidence values: {confidence_values}, '
            f'input: {input_str}'
        )

        if detected_language_code != language.short_name.lower():
            raise serializers.ValidationError(
                {
                    'check': {
                        'result': False,
                        'detected_language': detected_language_code,
                        'message': f'The detected language is "{detected_language.name.capitalize()}" ({detected_language_code}), '
                        f'which does not match your selected language "{language.full_name.capitalize()}" '
                        f'({language.short_name}). If you believe this is incorrect, try adding more content '
                        f'or rephrasing your text, as language detection works better with longer or more '
                        f'complete sentences.',
                    }
                }
            )

        return super().validate(data)
