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

from wger.exercises.api.serializers import ExerciseImageSerializer
from wger.exercises.models import Exercise
from wger.exercises.models import Equipment
from wger.exercises.models import ExerciseCategory
from wger.exercises.models import ExerciseImage
from wger.exercises.models import ExerciseComment
from wger.exercises.models import Muscle


class ExerciseViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for workout objects
    '''
    model = Exercise

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return Exercise.objects.all()


class EquipmentViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for workout objects
    '''
    model = Equipment

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return Equipment.objects.all()


class ExerciseCategoryViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for workout objects
    '''
    model = ExerciseCategory

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return ExerciseCategory.objects.all()


class ExerciseImageViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for exercise image objects
    '''
    model = ExerciseImage

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return ExerciseImage.objects.all()

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
        return Response(thumbnails)


class ExerciseCommentViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for workout objects
    '''
    model = ExerciseComment

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return ExerciseComment.objects.all()


class MuscleViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for workout objects
    '''
    model = Muscle

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return Muscle.objects.all()