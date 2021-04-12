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

# Standard Library
import logging

# Django
from django.utils.translation import gettext as _

# Third Party
from easy_thumbnails.alias import aliases
from easy_thumbnails.files import get_thumbnailer
from rest_framework import viewsets
from rest_framework.decorators import (
    action,
    api_view
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

# wger
from wger.config.models import LanguageConfig
from wger.exercises.api.serializers import (
    EquipmentSerializer,
    ExerciseBaseSerializer,
    ExerciseCategorySerializer,
    ExerciseCommentSerializer,
    ExerciseImageSerializer,
    ExerciseInfoSerializer,
    ExerciseSerializer,
    MuscleSerializer
)
from wger.exercises.models import (
    Equipment,
    Exercise,
    ExerciseCategory,
    ExerciseComment,
    ExerciseImage,
    Muscle
)
from wger.utils.language import (
    load_item_languages,
    load_language
)
from wger.utils.permissions import CreateOnlyPermission


logger = logging.getLogger(__name__)


class ExerciseBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for exercise base objects. For a read-only endpoint with all
    the information of an exercise, see /api/v2/exerciseinfo/
    """
    queryset = Exercise.objects.accepted()
    serializer_class = ExerciseBaseSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, CreateOnlyPermission)
    ordering_fields = '__all__'
    filterset_fields = ('category',
                        'muscles',
                        'muscles_secondary',
                        'equipment')


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for exercise objects. For a read-only endpoint with all
    the information of an exercise, see /api/v2/exerciseinfo/
    """
    queryset = Exercise.objects.accepted()
    serializer_class = ExerciseSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, CreateOnlyPermission)
    ordering_fields = '__all__'
    filterset_fields = ('uuid',
                        'creation_date',
                        'description',
                        'language',
                        'status',
                        'name')

    def perform_create(self, serializer):
        """
        Set author and status
        """
        language = load_language()
        obj = serializer.save(language=language)
        # Todo is it right to call set author after save?
        obj.set_author(self.request)
        obj.save()

    def get_queryset(self):
        """Add additional filters for fields from exercise base"""

        qs = Exercise.objects.accepted()

        category = self.request.query_params.get('category')
        muscles = self.request.query_params.get('muscles')
        muscles_secondary = self.request.query_params.get('muscles_secondary')
        equipment = self.request.query_params.get('equipment')
        license = self.request.query_params.get('license')

        if category:
            try:
                qs = qs.filter(exercise_base__category_id=int(category))
            except ValueError:
                logger.info(f"Got {category} as category ID")

        if muscles:
            try:
                qs = qs.filter(exercise_base__muscles__in=[int(m) for m in muscles.split(',')])
            except ValueError:
                logger.info(f"Got {muscles} as muscle IDs")

        if muscles_secondary:
            try:
                muscle_ids = [int(m) for m in muscles_secondary.split(',')]
                qs = qs.filter(exercise_base__muscles_secondary__in=muscle_ids)
            except ValueError:
                logger.info(f"Got '{muscles_secondary}' as secondary muscle IDs")

        if equipment:
            try:
                qs = qs.filter(exercise_base__equipment__in=[int(e) for e in equipment.split(',')])
            except ValueError:
                logger.info(f"Got {equipment} as equipment IDs")

        if license:
            try:
                qs = qs.filter(exercise_base__license_id=int(license))
            except ValueError:
                logger.info(f"Got {license} as license ID")

        return qs


@api_view(['GET'])
def search(request):
    """
    Searches for exercises.

    This format is currently used by the exercise search autocompleter
    """
    q = request.GET.get('term', None)
    results = []
    json_response = {}

    if q:
        languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES,
                                        language_code=request.GET.get('language', None))
        exercises = (Exercise.objects.filter(name__icontains=q)
                     .filter(language__in=languages)
                     .filter(status=Exercise.STATUS_ACCEPTED)
                     .order_by('exercise_base__category__name', 'name')
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

            exercise_json = {
                'value': exercise.name,
                'data': {
                    'id': exercise.id,
                    'name': exercise.name,
                    'category': _(exercise.category.name),
                    'image': image,
                    'image_thumbnail': thumbnail
                }
            }
            results.append(exercise_json)
        json_response['suggestions'] = results

    return Response(json_response)


class ExerciseInfoViewset(viewsets.ReadOnlyModelViewSet):
    """
    Read-only info API endpoint for exercise objects. Returns nested data
    structures for more easy parsing.
    """

    queryset = Exercise.objects.accepted()
    serializer_class = ExerciseInfoSerializer
    ordering_fields = '__all__'
    filterset_fields = ('creation_date',
                        'description',
                        'language',
                        'name',
                        'exercise_base',
                        'license',
                        'license_author')


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for equipment objects
    """
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    ordering_fields = '__all__'
    filterset_fields = ('name',)


class ExerciseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for exercise categories objects
    """
    queryset = ExerciseCategory.objects.all()
    serializer_class = ExerciseCategorySerializer
    ordering_fields = '__all__'
    filterset_fields = ('name',)


class ExerciseImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for exercise image objects
    """
    queryset = ExerciseImage.objects.all()
    serializer_class = ExerciseImageSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, CreateOnlyPermission)
    ordering_fields = '__all__'
    filterset_fields = ('is_main',
                        'status',
                        'exercise',
                        'license',
                        'license_author')

    @action(detail=True)
    def thumbnails(self, request, pk):
        """
        Return a list of the image's thumbnails
        """
        try:
            image = ExerciseImage.objects.get(pk=pk)
        except ExerciseImage.DoesNotExist:
            return Response([])

        thumbnails = {}
        for alias in aliases.all():
            t = get_thumbnailer(image.image)
            thumbnails[alias] = {
                'url': t.get_thumbnail(aliases.get(alias)).url,
                'settings': aliases.get(alias)
            }
        thumbnails['original'] = image.image.url
        return Response(thumbnails)

    def perform_create(self, serializer):
        """
        Set the license data
        """
        obj = serializer.save()
        # Todo is it right to call set author after save?
        obj.set_author(self.request)
        obj.save()


class ExerciseCommentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for exercise comment objects
    """
    serializer_class = ExerciseCommentSerializer
    ordering_fields = '__all__'
    filterset_fields = ('comment',
                        'exercise')

    def get_queryset(self):
        """Filter by language for exercise comments"""
        qs = ExerciseComment.objects.all()
        language = self.request.query_params.get('language')
        if language:
            exercises = Exercise.objects.filter(language=language)
            qs = ExerciseComment.objects.filter(exercise__in=exercises)
        return qs


class MuscleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for muscle objects
    """
    queryset = Muscle.objects.all()
    serializer_class = MuscleSerializer
    ordering_fields = '__all__'
    filterset_fields = ('name',
                        'is_front')
