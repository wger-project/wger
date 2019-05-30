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
    ExerciseCategory,
    ExerciseComment,
    ExerciseImage,
    Muscle
)


class ExerciseSerializer(serializers.ModelSerializer):
    '''
    Exercise serializer
    '''
    class Meta:
        model = Exercise
        fields = '__all__'


class EquipmentSerializer(serializers.ModelSerializer):
    '''
    Equipment serializer
    '''
    class Meta:
        model = Equipment
        fields = '__all__'


class ExerciseInfoSerializer(serializers.ModelSerializer):
    '''
    Equipment serializer
    '''
    class Meta:
        model = Exercise
        depth = 3
        fields = ("name", "category", "description", "muscles", "muscles_secondary", "equipment")


class ExerciseCategorySerializer(serializers.ModelSerializer):
    '''
    ExerciseCategory serializer
    '''
    class Meta:
        model = ExerciseCategory
        fields = '__all__'


class ExerciseImageSerializer(serializers.ModelSerializer):
    '''
    ExerciseImage serializer
    '''
    class Meta:
        model = ExerciseImage
        fields = '__all__'


class ExerciseCommentSerializer(serializers.ModelSerializer):
    '''
    ExerciseComment serializer
    '''
    class Meta:
        model = ExerciseComment
        fields = '__all__'


class MuscleSerializer(serializers.ModelSerializer):
    '''
    Muscle serializer
    '''
    class Meta:
        model = Muscle
        fields = '__all__'
