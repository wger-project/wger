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

from rest_framework import viewsets
from rest_framework.decorators import link
from rest_framework.response import Response
from easy_thumbnails.alias import aliases
from easy_thumbnails.files import get_thumbnailer

from wger.exercises.models import Exercise
from wger.exercises.models import Equipment
from wger.exercises.models import ExerciseCategory
from wger.exercises.models import ExerciseImage
from wger.exercises.models import ExerciseComment
from wger.exercises.models import Muscle


class ExerciseViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for exercise objects
    '''
    model = Exercise
    ordering_fields = '__all__'
    filter_fields = ('category',
                     'creation_date',
                     'description',
                     'language',
                     'muscles',
                     'status',
                     'name',
                     'license',
                     'license_author')

    def pre_save(self, obj):
        '''
        Set the license data
        '''
        if not obj.license_author:
            obj.license_author = self.request.user.username


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for equipment objects
    '''
    model = Equipment
    ordering_fields = '__all__'
    filter_fields = ('name',)


class ExerciseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for exercise categories objects
    '''
    model = ExerciseCategory
    ordering_fields = '__all__'
    filter_fields = ('name',)


class ExerciseImageViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for exercise image objects
    '''
    model = ExerciseImage
    ordering_fields = '__all__'
    filter_fields = ('image',
                     'is_main',
                     'license',
                     'license_author')

    @link()
    def thumbnails(self, request, pk):
        '''
        Return a list of the image's thumbnails
        '''
        image = ExerciseImage.objects.get(pk=pk)
        thumbnails = {}
        for alias in aliases.all():
            t = get_thumbnailer(image.image)
            thumbnails[alias] = {'url': t.get_thumbnail(aliases.get(alias)).url,
                                 'settings': aliases.get(alias)}
        thumbnails['original'] = image.image.url
        return Response(thumbnails)

    def pre_save(self, obj):
        '''
        Set the license data
        '''
        if not obj.license_author:
            obj.license_author = self.request.user.username


class ExerciseCommentViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for exercise comment objects
    '''
    model = ExerciseComment
    ordering_fields = '__all__'
    filter_fields = ('comment',
                     'exercise')


class MuscleViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for muscle objects
    '''
    model = Muscle
    ordering_fields = '__all__'
    filter_fields = ('name',
                     'is_front')
