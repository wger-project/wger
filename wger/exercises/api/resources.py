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
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from easy_thumbnails.alias import aliases
from easy_thumbnails.files import get_thumbnailer

from wger.core.api.resources import LanguageResource, LicenseResource

from wger.exercises.models import (
    Exercise,
    ExerciseCategory,
    ExerciseComment,
    ExerciseImage,
    Muscle,
    Equipment
)


class ExerciseResource(ModelResource):
    category = fields.ToOneField('wger.exercises.api.resources.ExerciseCategoryResource',
                                 'category')
    muscles = fields.ToManyField('wger.exercises.api.resources.MuscleResource', 'muscles')
    muscles_secondary = fields.ToManyField('wger.exercises.api.resources.MuscleResource',
                                           'muscles_secondary')
    comments = fields.ToManyField('wger.exercises.api.resources.ExerciseCommentResource',
                                  'exercisecomment_set')
    images = fields.ToManyField('wger.exercises.api.resources.ExerciseImageResource',
                                'exerciseimage_set')
    equipment = fields.ToManyField('wger.exercises.api.resources.EquipmentResource',
                                   'equipment')
    language = fields.ToOneField(LanguageResource, 'language')
    license = fields.ToOneField(LicenseResource, 'license')

    creation_date = fields.DateField(attribute='creation_date', null=True)

    class Meta:
        queryset = Exercise.objects.all()
        filtering = {'id': ALL,
                     "uuid": ALL,
                     "category": ALL_WITH_RELATIONS,
                     "creation_date": ALL,
                     "description": ALL,
                     "images": ALL_WITH_RELATIONS,
                     "language": ALL_WITH_RELATIONS,
                     "muscles": ALL_WITH_RELATIONS,
                     "status": ALL,
                     "name": ALL,
                     "license": ALL,
                     "license_author": ALL}


class EquipmentResource(ModelResource):

    class Meta:
        queryset = Equipment.objects.all()
        filtering = {'id': ALL,
                     "name": ALL}


class ExerciseCategoryResource(ModelResource):

    class Meta:
        queryset = ExerciseCategory.objects.all()
        filtering = {'id': ALL,
                     "name": ALL}


class ExerciseImageResource(ModelResource):
    exercise = fields.ToOneField('wger.exercises.api.resources.ExerciseResource', 'exercise')
    license = fields.ToOneField(LicenseResource, 'license')

    class Meta:
        queryset = ExerciseImage.objects.all()
        filtering = {'id': ALL,
                     "image": ALL,
                     "is_main": ALL,
                     "license": ALL,
                     "license_author": ALL}

    def dehydrate(self, bundle):
        '''
        Also send the URLs for the thumbnailed pictures
        '''
        thumbnails = {}
        for alias in aliases.all():
            t = get_thumbnailer(bundle.obj.image)
            thumbnails[alias] = {'url': t.get_thumbnail(aliases.get(alias)).url,
                                 'settings': aliases.get(alias)}

        bundle.data['thumbnails'] = thumbnails
        return bundle


class ExerciseCommentResource(ModelResource):
    exercise = fields.ToOneField('wger.exercises.api.resources.ExerciseResource', 'exercise')

    class Meta:
        queryset = ExerciseComment.objects.all()
        filtering = {'id': ALL,
                     "comment": ALL,
                     "exercise": ALL_WITH_RELATIONS}


class MuscleResource(ModelResource):
    class Meta:
        queryset = Muscle.objects.all()
        filtering = {'id': ALL,
                     "name": ALL,
                     "is_front": ALL}
