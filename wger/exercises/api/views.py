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
from uuid import UUID

# Django
from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page

# Third Party
import bleach
from actstream import action as actstream_action
from bleach.css_sanitizer import CSSSanitizer
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    inline_serializer,
)
from easy_thumbnails.alias import aliases
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer
from rest_framework import viewsets
from rest_framework.decorators import (
    action,
    api_view,
)
from rest_framework.fields import (
    CharField,
    IntegerField,
)
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
    ExerciseVariationSerializer,
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
    Variation,
)
from wger.exercises.views.helper import StreamVerbs
from wger.utils.constants import (
    ENGLISH_SHORT_NAME,
    HTML_ATTRIBUTES_WHITELIST,
    HTML_STYLES_WHITELIST,
    HTML_TAG_WHITELIST,
    SEARCH_ALL_LANGUAGES,
)
from wger.utils.db import is_postgres_db
from wger.utils.language import load_language


logger = logging.getLogger(__name__)


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
        super().perform_create(serializer)
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

        instance.delete(replace_by=uuid)


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
        # Clean the description HTML
        if serializer.validated_data.get('description'):
            serializer.validated_data['description'] = bleach.clean(
                serializer.validated_data['description'],
                tags=HTML_TAG_WHITELIST,
                attributes=HTML_ATTRIBUTES_WHITELIST,
                css_sanitizer=CSSSanitizer(allowed_css_properties=HTML_STYLES_WHITELIST),
                strip=True,
            )
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

        # Clean the description HTML
        if serializer.validated_data.get('description'):
            serializer.validated_data['description'] = bleach.clean(
                serializer.validated_data['description'],
                tags=HTML_TAG_WHITELIST,
                attributes=HTML_ATTRIBUTES_WHITELIST,
                css_sanitizer=CSSSanitizer(allowed_css_properties=HTML_STYLES_WHITELIST),
                strip=True,
            )

        super().perform_update(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.UPDATED.value,
            action_object=serializer.instance,
        )


@extend_schema(
    parameters=[
        OpenApiParameter(
            'term',
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description='The name of the exercise to search',
            required=True,
        ),
        OpenApiParameter(
            'language',
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description='Comma separated list of language codes to search',
            required=True,
        ),
    ],
    # yapf: disable
    responses={
        200: inline_serializer(
            name='ExerciseSearchResponse',
            fields={
                'value': CharField(),
                'data': inline_serializer(
                    name='ExerciseSearchItemResponse',
                    fields={
                        'id': IntegerField(),
                        'base_id': IntegerField(),
                        'name': CharField(),
                        'category': CharField(),
                        'image': CharField(),
                        'image_thumbnail': CharField(),
                    },
                ),
            },
        )
    },
    # yapf: enable
)
@api_view(['GET'])
def search(request):
    """
    Searches for exercises.

    This format is currently used by the exercise search autocompleter
    """
    q = request.GET.get('term', None)
    language_codes = request.GET.get('language', ENGLISH_SHORT_NAME)
    response = {}
    results = []

    if not q:
        return Response(response)

    # Filter the appropriate languages
    languages = [load_language(l) for l in language_codes.split(',')]
    if language_codes == SEARCH_ALL_LANGUAGES:
        query = Translation.objects.all()
    else:
        query = Translation.objects.filter(language__in=languages)

    query = query.only('name')

    # Postgres uses a full-text search
    if is_postgres_db():
        query = (
            query.annotate(similarity=TrigramSimilarity('name', q))
            .filter(Q(similarity__gt=0.15) | Q(alias__alias__icontains=q))
            .order_by('-similarity', 'name')
        )
    else:
        query = query.filter(Q(name__icontains=q) | Q(alias__alias__icontains=q))

    for translation in query:
        image = None
        thumbnail = None
        if translation.main_image:
            image_obj = translation.main_image
            image = image_obj.image.url
            t = get_thumbnailer(image_obj.image)
            thumbnail = None
            try:
                thumbnail = t.get_thumbnail(aliases.get('micro_cropped')).url
            except InvalidImageFormatError as e:
                logger.warning(f'InvalidImageFormatError while processing a thumbnail: {e}')
            except OSError as e:
                logger.warning(f'OSError while processing a thumbnail: {e}')

        result_json = {
            'value': translation.name,
            'data': {
                'id': translation.id,
                'base_id': translation.exercise_id,
                'name': translation.name,
                'category': _(translation.category.name),
                'image': image,
                'image_thumbnail': thumbnail,
            },
        }
        results.append(result_json)
    response['suggestions'] = results
    return Response(response)


class ExerciseInfoViewset(viewsets.ReadOnlyModelViewSet):
    """
    Read-only info API endpoint for exercise objects, grouped by the exercise
    base. Returns nested data structures for more easy and faster parsing and
    is the recommended way to access the exercise data.
    """

    queryset = Exercise.objects.all()
    serializer_class = ExerciseInfoSerializer
    ordering_fields = '__all__'
    filterset_class = ExerciseFilterSet
    filterset_fields = (
        'uuid',
        'category',
        'muscles',
        'muscles_secondary',
        'equipment',
        'variations',
        'license',
        'license_author',
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
        super().perform_create(serializer)
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
        super().perform_create(serializer)
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
        super().perform_create(serializer)
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
        super().perform_create(serializer)
        actstream_action.send(
            self.request.user,
            verb=StreamVerbs.UPDATED.value,
            action_object=serializer.instance,
        )


class ExerciseVariationViewSet(ModelViewSet):
    """
    API endpoint for exercise variation objects
    """

    serializer_class = ExerciseVariationSerializer
    queryset = Variation.objects.all()
    permission_classes = (CanContributeExercises,)


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
