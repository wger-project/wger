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
from uuid import UUID

# Django
from django.conf import settings
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Third Party
from actstream import action as actstream_action
from drf_spectacular.utils import extend_schema
from easy_thumbnails.alias import aliases
from easy_thumbnails.files import get_thumbnailer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# wger
from wger.exercises.api.filtersets import ExerciseFilterSet
from wger.exercises.api.permissions import CanContributeExercises
from wger.exercises.api.serializers import (
    DeletionLogSerializer,
    EquipmentSerializer,
    ExerciseAliasSerializer,
    ExerciseCategorySerializer,
    ExerciseCommentSerializer,
    ExerciseImageSerializer,
    ExerciseInfoSerializer,
    ExerciseSerializer,
    ExerciseSubmissionSerializer,
    ExerciseTranslationSerializer,
    ExerciseVideoSerializer,
    MuscleSerializer,
)
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


class ExerciseViewSet(ModelViewSet):
    """
    API endpoint for exercise objects.

    For a read-only endpoint with all the information of an exercise, see /api/v2/exerciseinfo/
    """

    queryset = Exercise.with_translations.all()
    serializer_class = ExerciseSerializer
    permission_classes = (CanContributeExercises,)
    ordering_fields = '__all__'
    filterset_fields = (
        'category',
        'muscles',
        'muscles_secondary',
        'equipment',
    )

    def perform_create(self, serializer):
        """
        Save entry to activity stream
        """
        super().perform_create(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.CREATED.value,
            action_object=serializer.instance,
        )

    def perform_update(self, serializer):
        """
        Save entry to activity stream
        """
        super().perform_update(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.UPDATED.value,
            action_object=serializer.instance,
        )

    def perform_destroy(self, instance: Exercise):
        """Manually delete the exercise and set the replacement, if any"""

        uuid = self.request.query_params.get('replaced_by', '')
        try:
            UUID(uuid, version=4)
        except ValueError:
            uuid = None

        transfer_media = 'transfer_media' in self.request.query_params
        transfer_translations = 'transfer_translations' in self.request.query_params

        replacement = Exercise.objects.filter(uuid=uuid).first() if uuid else None

        deleted_repr = str(instance)
        deleted_uuid = str(instance.uuid)

        instance.delete(
            replace_by=uuid,
            transfer_media=transfer_media,
            transfer_translations=transfer_translations,
        )

        if replacement:
            actstream_action.send(
                self.request.user,
                verb=StreamVerbs.MERGED.value,
                action_object=replacement,
                deleted_uuid=deleted_uuid,
                deleted_repr=deleted_repr,
                transfer_media=transfer_media,
                transfer_translations=transfer_translations,
            )
        else:
            actstream_action.send(
                self.request.user,
                verb=StreamVerbs.DELETED.value,
                deleted_uuid=deleted_uuid,
                deleted_repr=deleted_repr,
                model_type='exercise',
            )


class ExerciseTranslationViewSet(ModelViewSet):
    """
    API endpoint for editing or adding exercise translation objects.
    """

    queryset = Translation.objects.all()
    permission_classes = (CanContributeExercises,)
    serializer_class = ExerciseTranslationSerializer
    ordering_fields = '__all__'
    filterset_fields = (
        'uuid',
        'created',
        'exercise',
        'description',
        'name',
    )

    def perform_create(self, serializer):
        """
        Save entry to activity stream
        """

        super().perform_create(serializer)

        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.CREATED.value,
            action_object=serializer.instance,
        )

    def perform_update(self, serializer):
        """
        Save entry to activity stream
        """

        # Don't allow to change the base or the language over the API
        if serializer.validated_data.get('exercise'):
            del serializer.validated_data['exercise']

        if serializer.validated_data.get('language'):
            del serializer.validated_data['language']

        super().perform_update(serializer)

        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.UPDATED.value,
            action_object=serializer.instance,
        )


class ExerciseInfoViewset(viewsets.ReadOnlyModelViewSet):
    """
    Read-only info API endpoint for exercise objects, grouped by the exercise
    base. Returns nested data structures for more easy and faster parsing and
    is the recommended way to access the exercise data.
    """

    serializer_class = ExerciseInfoSerializer
    ordering_fields = '__all__'
    filterset_class = ExerciseFilterSet
    filterset_fields = (
        'uuid',
        'category',
        'muscles',
        'muscles_secondary',
        'equipment',
        'variation_group',
        'license',
        'license_author',
    )

    def get_queryset(self):
        """
        Optimize the queryset with select_related and prefetch_related to avoid
        n+1 queries

        One improvement is that we access the historical records of the exercise
        from the django-simple-history package, which are not really prefetchable
        since they are a manager.
        """

        return Exercise.objects.select_related(
            'category',
            'license',
        ).prefetch_related(
            'muscles',
            'muscles_secondary',
            'equipment',
            'exerciseimage_set',
            'exercisevideo_set',
            Prefetch(
                'translations',
                queryset=Translation.objects.prefetch_related('alias_set', 'exercisecomment_set'),
            ),
        )


class ExerciseSubmissionViewSet(CreateAPIView):
    """
    API endpoint for submitting new exercises
    """

    serializer_class = ExerciseSubmissionSerializer
    queryset = Exercise.objects.all()
    permission_classes = (CanContributeExercises,)


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for equipment objects
    """

    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    ordering_fields = '__all__'
    filterset_fields = ('name',)

    @method_decorator(cache_page(settings.WGER_SETTINGS['EXERCISE_CACHE_TTL']))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DeletionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for exercise deletion logs

    This lists objects that where deleted on a wger instance and should be deleted
    as well when performing a sync (e.g. because many exercises where submitted at
    once or an image was uploaded that hasn't a CC license)
    """

    queryset = DeletionLog.objects.all()
    serializer_class = DeletionLogSerializer
    ordering_fields = '__all__'
    filterset_fields = ('model_type',)


class ExerciseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for exercise categories objects
    """

    queryset = ExerciseCategory.objects.all()
    serializer_class = ExerciseCategorySerializer
    ordering_fields = '__all__'
    filterset_fields = ('name',)

    @method_decorator(cache_page(settings.WGER_SETTINGS['EXERCISE_CACHE_TTL']))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ExerciseImageViewSet(ModelViewSet):
    """
    API endpoint for exercise image objects
    """

    queryset = ExerciseImage.objects.all()
    serializer_class = ExerciseImageSerializer
    permission_classes = (CanContributeExercises,)
    ordering_fields = '__all__'
    filterset_fields = (
        'is_main',
        'exercise',
        'license',
        'license_author',
    )

    @method_decorator(cache_page(settings.WGER_SETTINGS['EXERCISE_CACHE_TTL']))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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
                'settings': aliases.get(alias),
            }
        thumbnails['original'] = image.image.url
        return Response(thumbnails)

    def perform_create(self, serializer):
        """
        Save entry to activity stream
        """
        super().perform_create(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.CREATED.value,
            action_object=serializer.instance,
        )

    def perform_update(self, serializer):
        """
        Save entry to activity stream
        """
        super().perform_update(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.UPDATED.value,
            action_object=serializer.instance,
        )


class ExerciseVideoViewSet(ModelViewSet):
    """
    API endpoint for exercise video objects
    """

    queryset = ExerciseVideo.objects.all()
    serializer_class = ExerciseVideoSerializer
    permission_classes = (CanContributeExercises,)
    ordering_fields = '__all__'
    filterset_fields = (
        'is_main',
        'exercise',
        'license',
        'license_author',
    )

    def perform_create(self, serializer):
        """
        Save entry to activity stream
        """
        super().perform_create(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.CREATED.value,
            action_object=serializer.instance,
        )

    def perform_update(self, serializer):
        """
        Save entry to activity stream
        """
        super().perform_update(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.UPDATED.value,
            action_object=serializer.instance,
        )


class ExerciseCommentViewSet(ModelViewSet):
    """
    API endpoint for exercise comment objects
    """

    serializer_class = ExerciseCommentSerializer
    permission_classes = (CanContributeExercises,)
    ordering_fields = '__all__'
    filterset_fields = ('comment', 'translation')

    def get_queryset(self):
        """Filter by language for exercise comments"""
        qs = ExerciseComment.objects.all()
        language = self.request.query_params.get('language')
        if language:
            translations = Translation.objects.filter(language=language)
            qs = ExerciseComment.objects.filter(translation__in=translations)
        return qs

    def perform_create(self, serializer):
        """
        Save entry to activity stream
        """
        super().perform_create(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.CREATED.value,
            action_object=serializer.instance,
        )

    def perform_update(self, serializer):
        """
        Save entry to activity stream
        """
        super().perform_update(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.UPDATED.value,
            action_object=serializer.instance,
        )


class ExerciseAliasViewSet(ModelViewSet):
    """
    API endpoint for exercise aliases objects
    """

    serializer_class = ExerciseAliasSerializer
    queryset = Alias.objects.all()
    permission_classes = (CanContributeExercises,)
    ordering_fields = '__all__'
    filterset_fields = ('alias', 'translation')

    def perform_create(self, serializer):
        """
        Save entry to activity stream
        """
        super().perform_create(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.CREATED.value,
            action_object=serializer.instance,
        )

    def perform_update(self, serializer):
        """
        Save entry to activity stream
        """
        super().perform_update(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.UPDATED.value,
            action_object=serializer.instance,
        )


class MuscleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for muscle objects
    """

    queryset = Muscle.objects.all()
    serializer_class = MuscleSerializer
    ordering_fields = '__all__'
    filterset_fields = ('name', 'is_front', 'name_en')

    @method_decorator(cache_page(settings.WGER_SETTINGS['EXERCISE_CACHE_TTL']))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
