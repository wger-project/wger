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

# Standard Library
import logging
import uuid

# Django
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q

# Third Party
from actstream import action as actstream_action
from rest_framework import serializers

# wger
from wger.core.models import License
from wger.exercises.api.validators import validate_language_matches
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
)
from wger.exercises.views.helper import StreamVerbs
from wger.utils.cache import CacheKeyMapper
from wger.utils.constants import CC_BY_SA_4_LICENSE_ID


logger = logging.getLogger(__name__)


def _log_action_creation(serializer, instance):
    """
    Emit an actstream ``created`` event for a freshly-created instance.

    Used by the submission serializers, which create nested objects directly
    instead of going through the regular ViewSet ``perform_create`` path.
    """
    request = serializer.context.get('request')
    if request is None or not getattr(request.user, 'is_authenticated', False):
        return
    actstream_action.send(
        request.user,
        verb=StreamVerbs.CREATED.value,
        action_object=instance,
    )


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
            'variation_group',
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
            'is_ai_generated',
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

    def validate(self, data):
        comment = data.get('comment')
        translation = data.get('translation') or (self.instance and self.instance.translation)
        if comment and translation:
            validate_language_matches(comment, translation.language, 'comment')
        return super().validate(data)


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

    image_url_main = serializers.SerializerMethodField()
    image_url_secondary = serializers.SerializerMethodField()

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

    def get_image_url_main(self, obj: Muscle):
        """Build absolute URL to muscle image"""

        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.image_url_main)

        # no host available
        logger.info('Cannot build absolute URL for main muscle image without request context')
        return None

    def get_image_url_secondary(self, obj: Muscle):
        """Build absolute URL to muscle image"""

        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.image_url_secondary)

        # no host available
        logger.info('Cannot build absolute URL for secondary muscle image without request context')
        return None


class ExerciseTranslationInfoSerializer(serializers.ModelSerializer):
    """
    Exercise translation serializer for the info endpoint
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
            'description_source',
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


class ExerciseTranslationSerializer(serializers.ModelSerializer):
    """
    Exercise translation serializer
    """

    id = serializers.IntegerField(required=False, read_only=True)
    uuid = serializers.UUIDField(required=False, read_only=True)
    description_source = serializers.CharField(required=False, allow_blank=True)
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
            'description_source',
            'created',
            'language',
            'license_author',
        )
        read_only_fields = ('description',)  # Prevents API from accepting raw HTML

    def validate(self, value):
        """
        Check that there is only one language per exercise, and that the
        detected language of the description matches the declared language.
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
            # -> Check if the language already exists. When ``exercise`` isn't
            # in the payload (submission flow creates a fresh exercise), the
            # check can't run and isn't relevant and there are no duplicates
            # by definition.
            elif value.get('exercise'):
                if Translation.objects.filter(
                    exercise=value['exercise'],
                    language=value['language'],
                ).exists():
                    raise serializers.ValidationError(
                        f'There is already a translation for this exercise in {value["language"]}'
                    )

        # Verify the detected language of the description matches the declared
        # language. On PATCH either field may be absent, so we fall back to the
        # persisted value where available.
        description = value.get('description_source')
        language = value.get('language') or (self.instance and self.instance.language)
        if description and language:
            validate_language_matches(description, language, 'description')

        return super().validate(value)


class ExerciseTranslationSubmissionSerializer(ExerciseTranslationSerializer):
    """
    Translation serializer used as a nested child of ``ExerciseSubmissionSerializer``.

    Differs from the regular serializer only because:
    - the ``exercise`` FK isn't known until the parent creates it (passed via ``create()`` kwargs);
    - the payload also accepts nested ``aliases`` and ``comments`` lists,
      which the regular CRUD endpoint doesn't.
    """

    aliases = ExerciseAliasSerializer(many=True, required=False)
    comments = ExerciseCommentSerializer(many=True, required=False)

    class Meta(ExerciseTranslationSerializer.Meta):
        fields = (
            'name',
            'description_source',
            'language',
            'aliases',
            'comments',
            'license_author',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ``translation`` is assigned by the parent submission in create()
        for nested in ('aliases', 'comments'):
            self.fields[nested].child.fields.pop('translation', None)

    def validate(self, data):
        data = super().validate(data)

        # Language of each child comment must also match the one in the declared translation
        language = data.get('language')
        if language:
            for comment_data in data.get('comments', []):
                comment_text = comment_data.get('comment')
                if comment_text:
                    validate_language_matches(comment_text, language, 'comment')

        return data

    def create(self, validated_data, **kwargs):
        aliases_data = validated_data.pop('aliases', [])
        comments_data = validated_data.pop('comments', [])
        exercise = kwargs.get('exercise')
        if not exercise:
            raise serializers.ValidationError(
                'Exercise is required to create a translation via submission.'
            )
        validated_data['exercise'] = exercise

        translation = Translation.objects.create(**validated_data)
        _log_action_creation(self, translation)

        for alias_data in aliases_data:
            alias = Alias.objects.create(translation=translation, **alias_data)
            _log_action_creation(self, alias)

        for comment_data in comments_data:
            comment = ExerciseComment.objects.create(translation=translation, **comment_data)
            _log_action_creation(self, comment)

        return translation


class ExerciseInfoSerializer(serializers.ModelSerializer):
    """
    Exercise info serializer
    """

    images = ExerciseImageSerializer(source='exerciseimage_set', many=True, read_only=True)
    category = ExerciseCategorySerializer(read_only=True)
    muscles = MuscleSerializer(many=True, read_only=True)
    muscles_secondary = MuscleSerializer(many=True, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    translations = ExerciseTranslationInfoSerializer(many=True, read_only=True)
    videos = ExerciseVideoInfoSerializer(source='exercisevideo_set', many=True, read_only=True)
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
            'variation_group',
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
    variation_group = serializers.UUIDField(
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
            'variation_group',
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

        # Either variation_group or variations_connect_to may be set, not both
        if data.get('variation_group') and data.get('variations_connect_to'):
            raise serializers.ValidationError(
                {
                    'variation_group': 'Either set variation_group or variations_connect_to, not both.'
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
            variation_group=validated_data.pop('variation_group', None),
        )
        exercise.muscles.set(validated_data.pop('muscles'))
        exercise.muscles_secondary.set(validated_data.pop('muscles_secondary'))
        exercise.equipment.set(validated_data.pop('equipment'))
        _log_action_creation(self, exercise)

        # Create the individual translations
        for translation in validated_data.pop('translations', []):
            serializer: ExerciseTranslationSubmissionSerializer = self.fields['translations'].child
            serializer.create(validated_data=translation, exercise=exercise)

        # If requested, add the exercise to an existing or new variation group
        connect_to: Exercise | None = validated_data.get('variations_connect_to')
        if connect_to:
            # Reuse the target's existing group, or create a new one
            group = connect_to.variation_group or uuid.uuid4()

            if not connect_to.variation_group:
                connect_to.variation_group = group
                connect_to.save()

            exercise.variation_group = group
            exercise.save()

        return exercise
