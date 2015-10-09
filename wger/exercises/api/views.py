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
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import detail_route, api_view

from easy_thumbnails.alias import aliases
from easy_thumbnails.files import get_thumbnailer

from django.utils.translation import ugettext as _

from wger.config.models import LanguageConfig
from wger.exercises.api.serializers import (
    MuscleSerializer,
    ExerciseSerializer,
    ExerciseImageSerializer,
    ExerciseCategorySerializer,
    EquipmentSerializer,
    ExerciseCommentSerializer
)
from wger.exercises.models import (
    Exercise,
    Equipment,
    ExerciseCategory,
    ExerciseImage,
    ExerciseComment,
    Muscle
)
from wger.utils.language import load_item_languages, load_language
from wger.utils.permissions import CreateOnlyPermission


class ExerciseViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for exercise objects
    '''
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, CreateOnlyPermission)
    ordering_fields = '__all__'
    filter_fields = ('category',
                     'creation_date',
                     'description',
                     'language',
                     'muscles',
                     'muscles_secondary',
                     'status',
                     'name',
                     'equipment',
                     'license',
                     'license_author')

    def perform_create(self, serializer):
        '''
        Set author and status
        '''
        language = load_language()
        obj = serializer.save(language=language)
        # Todo is it right to call set author after save?
        obj.set_author(self.request)
        obj.save()


@api_view(['GET'])
def search(request):
    '''
    Searches for exercises.

    This format is currently used by the exercise search autocompleter
    '''
    q = request.GET.get('term', None)
    results = []
    if not q:
        return Response(results)

    languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)
    exercises = (Exercise.objects.filter(name__icontains=q)
                                 .filter(language__in=languages)
                                 .filter(status=Exercise.STATUS_ACCEPTED)
                                 .order_by('category__name', 'name')
                                 .distinct())

    for exercise in exercises:
        if exercise.main_image:
            image_obj = exercise.main_image
            image = image_obj.image.url
            t = get_thumbnailer(image_obj.image)
            thumbnail = t.get_thumbnail(aliases.get('micro_cropped')).url
        else:
            image = None
            thumbnail = None

        exercise_json = {'id': exercise.id,
                         'name': exercise.name,
                         'value': exercise.name,
                         'category': _(exercise.category.name),
                         'image': image,
                         'image_thumbnail': thumbnail}

        results.append(exercise_json)

    return Response(results)


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for equipment objects
    '''
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    ordering_fields = '__all__'
    filter_fields = ('name',)


class ExerciseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for exercise categories objects
    '''
    queryset = ExerciseCategory.objects.all()
    serializer_class = ExerciseCategorySerializer
    ordering_fields = '__all__'
    filter_fields = ('name',)


class ExerciseImageViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for exercise image objects
    '''
    queryset = ExerciseImage.objects.all()
    serializer_class = ExerciseImageSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, CreateOnlyPermission)
    ordering_fields = '__all__'
    filter_fields = ('is_main',
                     'status',
                     'exercise',
                     'license',
                     'license_author')

    @detail_route()
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

    def perform_create(self, serializer):
        '''
        Set the license data
        '''
        obj = serializer.save()
        # Todo is it right to call set author after save?
        obj.set_author(self.request)
        obj.save()


class ExerciseCommentViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for exercise comment objects
    '''
    queryset = ExerciseComment.objects.all()
    serializer_class = ExerciseCommentSerializer
    ordering_fields = '__all__'
    filter_fields = ('comment',
                     'exercise')


class MuscleViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for muscle objects
    '''
    queryset = Muscle.objects.all()
    serializer_class = MuscleSerializer
    ordering_fields = '__all__'
    filter_fields = ('name',
                     'is_front')
