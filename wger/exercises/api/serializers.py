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

# Django
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q

# Third Party
from lingua import LanguageDetectorBuilder
from rest_framework import serializers

# wger
from wger.core.models import (
    Language,
    License,
)
from wger.exercises.models import (
    Alias,
    DeletionLog,
    Equipment,
    Exercise,
    ExerciseCategory,
    ExerciseComment,
    ExerciseImage,
    ExerciseVideo,
    Muscle,
    Translation,
    Variation,
)
from wger.utils.cache import CacheKeyMapper
from wger.utils.constants import CC_BY_SA_4_LICENSE_ID


class ExerciseSerializer(serializers.ModelSerializer):
    """
    Exercise serializer
    """

    class Meta:
        model = Exercise
        fields = (
            'id',
            'uuid',
            'created',
            'last_update',
            'category',
            'muscles',
            'muscles_secondary',
            'equipment',
            'variations',
            'license_author',
        )


class EquipmentSerializer(serializers.ModelSerializer):
    """
    Equipment serializer
    """

    class Meta:
        model = Equipment
        fields = ('id', 'name')


class DeletionLogSerializer(serializers.ModelSerializer):
    """
    Deletion log serializer
    """

    class Meta:
        model = DeletionLog
        fields = (
            'model_type',
            'uuid',
            'replaced_by',
            'timestamp',
            'comment',
        )


class ExerciseImageSerializer(serializers.ModelSerializer):
    """
    ExerciseImage serializer
    """

    author_history = serializers.ListSerializer(child=serializers.CharField(), read_only=True)
    exercise_uuid = serializers.ReadOnlyField(source='exercise.uuid')

    class Meta:
        model = ExerciseImage
        fields = (
            'id',
            'uuid',
            'exercise',
            'exercise_uuid',
            'image',
            'is_main',
            'style',
            'license',
            'license_title',
            'license_object_url',
            'license_author',
            'license_author_url',
            'license_derivative_source_url',
            'author_history',
        )


class ExerciseVideoSerializer(serializers.ModelSerializer):
    """
    ExerciseVideo serializer
    """

    exercise_uuid = serializers.ReadOnlyField(source='exercise.uuid')
    author_history = serializers.ListSerializer(child=serializers.CharField(), read_only=True)

    class Meta:
        model = ExerciseVideo
        fields = (
            'id',
            'uuid',
            'exercise',
            'exercise_uuid',
            'video',
            'is_main',
            'size',
            'duration',
            'width',
            'height',
            'codec',
            'codec_long',
            'license',
            'license_title',
            'license_object_url',
            'license_author',
            'license_author_url',
            'license_derivative_source_url',
            'author_history',
        )


class ExerciseVideoInfoSerializer(serializers.ModelSerializer):
    """
    ExerciseVideo serializer for the info endpoint
    """

    author_history = serializers.ListSerializer(child=serializers.CharField(), read_only=True)

    class Meta:
        model = ExerciseVideo
        fields = (
            'id',
            'uuid',
            'exercise',
            'video',
            'is_main',
            'size',
            'duration',
            'width',
            'height',
            'codec',
            'codec_long',
            'license',
            'license_title',
            'license_object_url',
            'license_author',
            'license_author_url',
            'license_derivative_source_url',
            'author_history',
        )


class ExerciseCommentSerializer(serializers.ModelSerializer):
    """
    ExerciseComment serializer
    """

    id = serializers.IntegerField(required=False, read_only=True)

    class Meta:
        model = ExerciseComment
        fields = (
            'id',
            'uuid',
            'translation',
            'comment',
        )


class ExerciseCommentSubmissionSerializer(serializers.ModelSerializer):
    """
    ExerciseComment submission serializer
    """

    class Meta:
        model = ExerciseComment
        fields = ('comment',)

    def create(self, validated_data, **kwargs):
        """
        Custom create-method to handle the 'translation' keyword argument
        and set the foreign key relationship.
        """
        translation: Translation = kwargs.get('translation')
        if not translation:
            raise serializers.ValidationError(
                'A translation object is required for creating a comment.'
            )

        # Validate the language of the description
        # -> This is done here instead of in the serializer's validate method
        #    because the language is not available in the serializer's initial_data
        detector = (
            LanguageDetectorBuilder.from_all_languages()
            .with_low_accuracy_mode()
            .with_preloaded_language_models()
            .build()
        )
        language = translation.language

        # Try to detect the language
        detected_language = detector.detect_language_of(validated_data['comment'])
        detected_language_code = detected_language.iso_code_639_1.name.lower()
        if detected_language_code != language.short_name.lower():
            raise serializers.ValidationError(
                {
                    'language': f'The detected language of the comment is "{detected_language.name.capitalize()}" '
                    f'({detected_language_code}), which does not match your selected language: '
                    f'"{language.full_name.capitalize()}" ({language.short_name}). If you believe '
                    f'this is incorrect, try adding more content or rephrasing your text, as '
                    f'language detection works better with longer or more complete sentences.'
                }
            )

        # Create the comment with the parent translation
        comment = ExerciseComment.objects.create(translation=translation, **validated_data)
        return comment


class ExerciseAliasSerializer(serializers.ModelSerializer):
    """
    ExerciseAlias serializer
    """

    class Meta:
        model = Alias
        fields = (
            'id',
            'uuid',
            'translation',
            'alias',
        )


class ExerciseAliasSubmissionSerializer(serializers.ModelSerializer):
    """
    ExerciseAlias submission serializer
    """

    class Meta:
        model = Alias
        fields = ('alias',)

    def create(self, validated_data, **kwargs):
        """
        Custom create-method to handle the 'translation' keyword argument
        and set the foreign key relationship.
        """
        translation = kwargs.get('translation')
        if not translation:
            raise serializers.ValidationError(
                'A translation object is required for creating an alias.'
            )

        # Create the Alias with the parent translation
        alias = Alias.objects.create(translation=translation, **validated_data)
        return alias


class ExerciseVariationSerializer(serializers.ModelSerializer):
    """
    Exercise variation serializer
    """

    class Meta:
        model = Variation
        fields = ('id',)


class ExerciseInfoAliasSerializer(serializers.ModelSerializer):
    """
    Exercise alias serializer for info endpoint
    """

    class Meta:
        model = Alias
        fields = (
            'id',
            'uuid',
            'alias',
        )


class ExerciseCategorySerializer(serializers.ModelSerializer):
    """
    ExerciseCategory serializer
    """

    class Meta:
        model = ExerciseCategory
        fields = ('id', 'name')


class MuscleSerializer(serializers.ModelSerializer):
    """
    Muscle serializer
    """

    image_url_main = serializers.CharField()
    image_url_secondary = serializers.CharField()

    class Meta:
        model = Muscle
        fields = (
            'id',
            'name',
            'name_en',
            'is_front',
            'image_url_main',
            'image_url_secondary',
        )


class ExerciseTranslationBaseInfoSerializer(serializers.ModelSerializer):
    """
    Exercise translation serializer for the base info endpoint
    """

    id = serializers.IntegerField(required=False, read_only=True)
    uuid = serializers.UUIDField(required=False, read_only=True)
    exercise = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        required=True,
    )
    aliases = ExerciseInfoAliasSerializer(source='alias_set', many=True, read_only=True)
    notes = ExerciseCommentSerializer(source='exercisecomment_set', many=True, read_only=True)
    author_history = serializers.ListSerializer(child=serializers.CharField())

    class Meta:
        model = Translation
        fields = (
            'id',
            'uuid',
            'name',
            'exercise',
            'description',
            'created',
            'language',
            'aliases',
            'notes',
            'license',
            'license_title',
            'license_object_url',
            'license_author',
            'license_author_url',
            'license_derivative_source_url',
            'author_history',
        )


class ExerciseTranslationSubmissionSerializer(serializers.ModelSerializer):
    """
    Exercise translation submission serializer
    """

    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all())
    aliases = ExerciseAliasSubmissionSerializer(many=True, required=False)
    comments = ExerciseCommentSubmissionSerializer(many=True, required=False)

    class Meta:
        model = Translation
        fields = (
            'name',
            'description',
            'language',
            'aliases',
            'comments',
            'license_author',
        )

    def validate(self, data):
        """
        Custom validator to ensure the detected language of the description corresponds with the
        provided language.
        """
        detector = (
            LanguageDetectorBuilder.from_all_languages()
            .with_low_accuracy_mode()
            .with_preloaded_language_models()
            .build()
        )

        language = data.get('language')
        description = data.get('description')

        # Try to detect the language
        detected_language = detector.detect_language_of(description)
        detected_language_code = detected_language.iso_code_639_1.name.lower()
        if detected_language_code != language.short_name.lower():
            raise serializers.ValidationError(
                {
                    'language': f'The detected language of the description is "{detected_language.name.capitalize()}" '
                    f'({detected_language_code}), which does not match your selected language: '
                    f'"{language.full_name.capitalize()}" ({language.short_name}). If you believe '
                    f'this is incorrect, try adding more content or rephrasing your text, as '
                    f'language detection works better with longer or more complete sentences.'
                }
            )

        return super().validate(data)

    def create(self, validated_data, **kwargs):
        """
        Custom create-method to handle the 'exercise' keyword argument
        and set the foreign key relationship.
        """
        aliases_data = validated_data.pop('aliases', [])
        comments_data = validated_data.pop('comments', [])
        exercise = kwargs.get('exercise')
        if not exercise:
            raise serializers.ValidationError(
                'Translation object is required for creating an Alias'
            )

        # Create the translation with the parent exercise
        translation = Translation.objects.create(exercise=exercise, **validated_data)

        # Create the individual aliases
        for alias_data in aliases_data:
            alias_serializer = self.fields['aliases'].child
            alias_serializer.create(validated_data=alias_data, translation=translation)

        # Create the individual comments
        for comment_data in comments_data:
            comment_serializer = self.fields['comments'].child
            comment_serializer.create(validated_data=comment_data, translation=translation)

        return translation


class ExerciseTranslationSerializer(serializers.ModelSerializer):
    """
    Exercise translation serializer
    """

    id = serializers.IntegerField(required=False, read_only=True)
    uuid = serializers.UUIDField(required=False, read_only=True)
    exercise = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        required=True,
    )

    class Meta:
        model = Translation
        fields = (
            'id',
            'uuid',
            'name',
            'exercise',
            'description',
            'created',
            'language',
            'license_author',
        )

    def validate(self, value):
        """
        Check that there is only one language per exercise
        """
        if value.get('language'):
            # Editing an existing object
            # -> Check if the language already exists, excluding the current object
            if self.instance:
                if self.instance.exercise.translations.filter(
                    ~Q(id=self.instance.pk),
                    language=value['language'],
                ).exists():
                    raise serializers.ValidationError(
                        f'There is already a translation for this exercise in {value["language"]}'
                    )
            # Creating a new object
            # -> Check if the language already exists
            else:
                if Translation.objects.filter(
                    exercise=value['exercise'],
                    language=value['language'],
                ).exists():
                    raise serializers.ValidationError(
                        f'There is already a translation for this exercise in {value["language"]}'
                    )

        return super().validate(value)


class ExerciseInfoSerializer(serializers.ModelSerializer):
    """
    Exercise info serializer
    """

    images = ExerciseImageSerializer(source='exerciseimage_set', many=True, read_only=True)
    category = ExerciseCategorySerializer(read_only=True)
    muscles = MuscleSerializer(many=True, read_only=True)
    muscles_secondary = MuscleSerializer(many=True, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    translations = ExerciseTranslationBaseInfoSerializer(many=True, read_only=True)
    videos = ExerciseVideoInfoSerializer(source='exercisevideo_set', many=True, read_only=True)
    variations = serializers.PrimaryKeyRelatedField(read_only=True)
    author_history = serializers.ListSerializer(child=serializers.CharField())
    total_authors_history = serializers.ListSerializer(child=serializers.CharField())
    last_update_global = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Exercise
        depth = 1
        fields = (
            'id',
            'uuid',
            'created',
            'last_update',
            'last_update_global',
            'category',
            'muscles',
            'muscles_secondary',
            'equipment',
            'license',
            'license_author',
            'images',
            'translations',
            'variations',
            'images',
            'videos',
            'author_history',
            'total_authors_history',
        )

    def to_representation(self, instance):
        """
        Cache the response
        """
        key = CacheKeyMapper.get_exercise_api_key(instance.uuid)

        representation = cache.get(key)
        if representation:
            return representation

        representation = super().to_representation(instance)
        cache.set(key, representation, settings.WGER_SETTINGS['EXERCISE_CACHE_TTL'])
        return representation


def get_default_license() -> License:
    return License.objects.get(pk=CC_BY_SA_4_LICENSE_ID)


class ExerciseSubmissionSerializer(serializers.ModelSerializer):
    """
    Exercise submission serializer
    """

    id = serializers.IntegerField(required=False, read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=ExerciseCategory.objects.all())
    muscles = serializers.PrimaryKeyRelatedField(
        queryset=Muscle.objects.all(),
        many=True,
        required=False,
        default=list,
    )
    muscles_secondary = serializers.PrimaryKeyRelatedField(
        queryset=Muscle.objects.all(),
        many=True,
        required=False,
        default=list,
    )
    equipment = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all(),
        many=True,
        required=False,
        default=list,
    )
    translations = ExerciseTranslationSubmissionSerializer(many=True)
    license = serializers.PrimaryKeyRelatedField(
        queryset=License.objects.all(),
        required=False,
        # Note, using a function here because of problems during tests
        default=get_default_license,
    )
    variations = serializers.PrimaryKeyRelatedField(
        queryset=Variation.objects.all(),
        required=False,
        allow_null=True,
    )
    variations_connect_to = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
        help_text='If provided, the created exercise will be added to the selected variation set.',
    )

    class Meta:
        fields = (
            'id',
            'category',
            'muscles',
            'muscles_secondary',
            'equipment',
            'variations',
            'variations_connect_to',
            'license',
            'license_author',
            'translations',
        )
        model = Exercise

    def validate(self, data):
        # Ensure at least one translation is present
        translations = data.get('translations', [])
        if not data.get('translations', []):
            raise serializers.ValidationError(
                {'translations': 'You must provide at least one translation.'}
            )

        # At least one translation in English
        if not any(t.get('language').short_name == 'en' for t in translations):
            raise serializers.ValidationError(
                {'translations': 'You must provide at least one translation in English.'}
            )

        # Either the variations or variations_connect_to field may be set, not both
        if data.get('variations') and data.get('variations_connect_to'):
            raise serializers.ValidationError(
                {
                    'variations': 'Either set the variations or the variations_connect_to field, not both.'
                }
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        # Create the Exercise object first
        exercise = Exercise.objects.create(
            category=validated_data.pop('category'),
            license=validated_data.pop('license'),
            license_author=validated_data.pop('license_author'),
            variations=validated_data.pop('variations', None),
        )
        exercise.muscles.set(validated_data.pop('muscles'))
        exercise.muscles_secondary.set(validated_data.pop('muscles_secondary'))
        exercise.equipment.set(validated_data.pop('equipment'))

        # Create the individual translations
        for translation in validated_data.pop('translations', []):
            serializer: ExerciseTranslationSubmissionSerializer = self.fields['translations'].child
            serializer.create(validated_data=translation, exercise=exercise)

        # If requested, add the exercise to an existing variation set
        connect_to: Exercise | None = validated_data.get('variations_connect_to')
        if connect_to:
            new_variation = Variation.objects.create()

            connect_to.variations = new_variation
            connect_to.save()

            exercise.variations = new_variation
            exercise.save()

        return exercise
