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

from tastypie import fields
from tastypie.resources import ModelResource

from wger.exercises.models import Exercise
from wger.exercises.models import ExerciseCategory
from wger.exercises.models import ExerciseComment
from wger.exercises.models import ExerciseImage
from wger.exercises.models import Muscle
from wger.exercises.models import Language


class ExerciseResource(ModelResource):
    category = fields.ToOneField('wger.exercises.api.resources.ExerciseCategoryResource',
                                 'category')
    muscles = fields.ToManyField('wger.exercises.api.resources.MuscleResource', 'muscles')
    comments = fields.ToManyField('wger.exercises.api.resources.ExerciseCommentResource',
                                  'exercisecomment_set')
    images = fields.ToManyField('wger.exercises.api.resources.ExerciseImageResource',
                                'exerciseimage_set')
    language = fields.ToOneField('wger.exercises.api.resources.LanguageResource', 'language')
    creation_date = fields.DateField(attribute='creation_date', null=True)

    class Meta:
        queryset = Exercise.objects.all()


class ExerciseCategoryResource(ModelResource):

    class Meta:
        queryset = ExerciseCategory.objects.all()


class ExerciseImageResource(ModelResource):
    exercise = fields.ToOneField('wger.exercises.api.resources.ExerciseResource', 'exercise')

    class Meta:
        queryset = ExerciseImage.objects.all()


class ExerciseCommentResource(ModelResource):
    exercise = fields.ToOneField('wger.exercises.api.resources.ExerciseResource', 'exercise')

    class Meta:
        queryset = ExerciseComment.objects.all()


class MuscleResource(ModelResource):
    class Meta:
        queryset = Muscle.objects.all()


class LanguageResource(ModelResource):
    class Meta:
        queryset = Language.objects.all()
