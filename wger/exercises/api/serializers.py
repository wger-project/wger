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
    Equipment,
    Exercise,
    ExerciseAlias,
    ExerciseBase,
    ExerciseCategory,
    ExerciseComment,
    ExerciseImage,
    Muscle,
    Variation,
)


class ExerciseBaseSerializer(serializers.ModelSerializer):
    """
    Exercise base serializer
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
        fields = ['id', 'name']


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


class ExerciseAliasSerializer(serializers.ModelSerializer):
    """
    ExerciseAlias serializer
    """

    class Meta:
        model = ExerciseAlias
        fields = ['id', 'exercise', 'alias']


class ExerciseVariationSerializer(serializers.ModelSerializer):
    """
    Exercise variation serializer
    """

    class Meta:
        model = Variation
        fields = [
            'id',
        ]


class ExerciseInfoAliasSerializer(serializers.ModelSerializer):
    """
    Exercise alias serializer for info endpoint
    """

    class Meta:
        model = ExerciseAlias
        fields = ['id', 'alias']


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
    category = serializers.PrimaryKeyRelatedField(queryset=ExerciseCategory.objects.all())
    muscles = serializers.PrimaryKeyRelatedField(many=True, queryset=Muscle.objects.all())
    muscles_secondary = serializers.PrimaryKeyRelatedField(many=True, queryset=Muscle.objects.all())
    equipment = serializers.PrimaryKeyRelatedField(many=True, queryset=Equipment.objects.all())
    variations = serializers.PrimaryKeyRelatedField(many=True, queryset=Variation.objects.all())

    class Meta:
        model = Exercise
        fields = (
            "id",
            "uuid",
            "name",
            "exercise_base",
            "status",
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


class ExerciseInfoSerializer(serializers.ModelSerializer):
    """
    Exercise info serializer
    """

    images = ExerciseImageSerializer(many=True, read_only=True)
    comments = ExerciseCommentSerializer(source='exercisecomment_set', many=True, read_only=True)
    category = ExerciseCategorySerializer(read_only=True)
    muscles = MuscleSerializer(many=True, read_only=True)
    muscles_secondary = MuscleSerializer(many=True, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    variations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    aliases = ExerciseInfoAliasSerializer(source='exercisealias_set', many=True, read_only=True)

    class Meta:
        model = Exercise
        depth = 1
        fields = [
            "id",
            "name",
            "aliases",
            "uuid",
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
            "comments",
            "variations",
        ]
