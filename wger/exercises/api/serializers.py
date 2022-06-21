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

# Third Party
from rest_framework import serializers

# wger
from wger.exercises.models import (
    Alias,
    Equipment,
    Exercise,
    ExerciseBase,
    ExerciseCategory,
    ExerciseComment,
    ExerciseImage,
    ExerciseVideo,
    Muscle,
)


class ExerciseBaseSerializer(serializers.ModelSerializer):
    """
    Exercise serializer
    """

    class Meta:
        model = ExerciseBase
        fields = [
            'id',
            'uuid',
            'creation_date',
            'update_date',
            'category',
            'muscles',
            'muscles_secondary',
            'equipment',
            'variations',
        ]


class EquipmentSerializer(serializers.ModelSerializer):
    """
    Equipment serializer
    """

    class Meta:
        model = Equipment
        fields = [
            'id',
            'name',
        ]


class ExerciseImageSerializer(serializers.ModelSerializer):
    """
    ExerciseImage serializer
    """

    class Meta:
        model = ExerciseImage
        fields = [
            'id',
            'uuid',
            'exercise_base',
            'image',
            'is_main',
            'status',
            'style',
        ]


class ExerciseVideoSerializer(serializers.ModelSerializer):
    """
    ExerciseVideo serializer
    """
    exercise_base_uuid = serializers.ReadOnlyField(source='exercise_base.uuid')

    class Meta:
        model = ExerciseVideo
        fields = [
            'id',
            'uuid',
            'exercise_base',
            'exercise_base_uuid',
            'video',
            'is_main',
            'size',
            'duration',
            'width',
            'height',
            'codec',
            'codec_long',
            'license',
            'license_author',
        ]


class ExerciseCommentSerializer(serializers.ModelSerializer):
    """
    ExerciseComment serializer
    """

    class Meta:
        model = ExerciseComment
        fields = [
            'id',
            'exercise',
            'comment',
        ]


class ExerciseInfoAliasSerializer(serializers.ModelSerializer):
    """
    Exercise alias serializer for info endpoint
    """

    class Meta:
        model = Alias
        fields = [
            'id',
            'alias',
        ]


class ExerciseCategorySerializer(serializers.ModelSerializer):
    """
    ExerciseCategory serializer
    """

    class Meta:
        model = ExerciseCategory
        fields = ['id', 'name']


class MuscleSerializer(serializers.ModelSerializer):
    """
    Muscle serializer
    """

    class Meta:
        model = Muscle
        fields = [
            'id',
            'name',
            'name_en',
            'is_front',
            'image_url_main',
            'image_url_secondary',
        ]


class ExerciseSerializer(serializers.ModelSerializer):
    """
    Exercise serializer

    The fields from the new ExerciseBase are retrieved here as to retain
    compatibility with the old model where all the fields where in Exercise.
    """
    category = serializers.PrimaryKeyRelatedField(read_only=True)
    muscles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    muscles_secondary = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    equipment = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    variations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Exercise
        fields = (
            "id",
            "uuid",
            "name",
            "exercise_base",
            "description",
            "creation_date",
            "category",
            "muscles",
            "muscles_secondary",
            "equipment",
            "language",
            "license",
            "license_author",
            "variations",
        )


class ExerciseTranslationSerializer(serializers.ModelSerializer):
    """
    Exercise translation serializer
    """

    id = serializers.IntegerField(required=False, read_only=True)
    uuid = serializers.UUIDField(required=False, read_only=True)
    aliases = ExerciseInfoAliasSerializer(source='alias_set', many=True, read_only=True)
    notes = ExerciseCommentSerializer(source='exercisecomment_set', many=True, read_only=True)

    class Meta:
        model = Exercise
        fields = (
            "id",
            "uuid",
            "aliases",
            "name",
            "description",
            "notes",
            "creation_date",
            "language",
            "license",
            "license_author",
        )


class ExerciseInfoSerializer(serializers.ModelSerializer):
    """
    Exercise info serializer
    """

    images = ExerciseImageSerializer(many=True, read_only=True)
    videos = ExerciseVideoSerializer(many=True, read_only=True)
    comments = ExerciseCommentSerializer(source='exercisecomment_set', many=True, read_only=True)
    category = ExerciseCategorySerializer(read_only=True)
    muscles = MuscleSerializer(many=True, read_only=True)
    muscles_secondary = MuscleSerializer(many=True, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    variations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Exercise
        depth = 1
        fields = [
            "id",
            "name",
            "uuid",
            "exercise_base_id",
            "description",
            "creation_date",
            "category",
            "muscles",
            "muscles_secondary",
            "equipment",
            "language",
            "license",
            "license_author",
            "images",
            "videos",
            "comments",
            "variations",
        ]


class ExerciseBaseInfoSerializer(serializers.ModelSerializer):
    """
    Exercise base info serializer
    """

    images = ExerciseImageSerializer(source='exerciseimage_set', many=True, read_only=True)
    category = ExerciseCategorySerializer(read_only=True)
    muscles = MuscleSerializer(many=True, read_only=True)
    muscles_secondary = MuscleSerializer(many=True, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    exercises = ExerciseTranslationSerializer(many=True, read_only=True)
    variations = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ExerciseBase
        depth = 1
        fields = [
            "id",
            "uuid",
            "category",
            "muscles",
            "muscles_secondary",
            "equipment",
            "license",
            "license_author",
            "images",
            "exercises",
            "variations",
            "images",
        ]
