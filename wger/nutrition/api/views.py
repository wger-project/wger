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
import datetime

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Third Party
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    inline_serializer,
)
from easy_thumbnails.alias import aliases
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
from rest_framework.response import Response

# wger
from wger.nutrition.api.serializers import (
    IngredientImageSerializer,
    IngredientInfoSerializer,
    IngredientSerializer,
    IngredientWeightUnitSerializer,
    LogItemSerializer,
    MealItemSerializer,
    MealSerializer,
    NutritionPlanInfoSerializer,
    NutritionPlanSerializer,
    WeightUnitSerializer,
)
from wger.nutrition.forms import UnitChooserForm
from wger.nutrition.models import (
    Image,
    Ingredient,
    IngredientWeightUnit,
    LogItem,
    Meal,
    MealItem,
    NutritionPlan,
    WeightUnit,
)
from wger.utils.constants import ENGLISH_SHORT_NAME
from wger.utils.language import load_language
from wger.utils.viewsets import WgerOwnerObjectModelViewSet


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for ingredient objects. For a read-only endpoint with all
    the information of an ingredient, see /api/v2/ingredientinfo/
    """
    queryset = Ingredient.objects.accepted()
    serializer_class = IngredientSerializer
    ordering_fields = '__all__'
    filterset_fields = (
        'uuid',
        'code',
        'carbohydrates',
        'carbohydrates_sugar',
        'creation_date',
        'energy',
        'fat',
        'fat_saturated',
        'fibres',
        'name',
        'protein',
        'sodium',
        'status',
        'update_date',
        'language',
        'license',
        'license_author',
    )

    @method_decorator(cache_page(settings.WGER_SETTINGS['EXERCISE_CACHE_TTL']))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def get_values(self, request, pk):
        """
        Calculates the nutritional values for current ingredient and
        the given amount and unit.

        This function basically just performs a multiplication (in the model), and
        is a candidate to be moved to pure AJAX calls, however doing it like this
        keeps the logic nicely hidden and respects the DRY principle.
        """

        result = {
            'energy': 0,
            'protein': 0,
            'carbohydrates': 0,
            'carbohydrates_sugar': 0,
            'fat': 0,
            'fat_saturated': 0,
            'fibres': 0,
            'sodium': 0,
            'errors': []
        }
        ingredient = self.get_object()

        form = UnitChooserForm(request.GET)

        if form.is_valid():

            # Create a temporary MealItem object
            if form.cleaned_data['unit']:
                unit_id = form.cleaned_data['unit'].id
            else:
                unit_id = None

            item = MealItem()
            item.ingredient = ingredient
            item.weight_unit_id = unit_id
            item.amount = form.cleaned_data['amount']

            result = item.get_nutritional_values()

            for i in result:
                result[i] = '{0:f}'.format(result[i])
        else:
            result['errors'] = form.errors

        return Response(result)


class IngredientInfoViewSet(IngredientViewSet):
    """
    Read-only info API endpoint for ingredient objects. Returns nested data
    structures for more easy parsing.
    """
    serializer_class = IngredientInfoSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            'term',
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description='The name of the ingredient to search"',
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
    responses={
        200:
        inline_serializer(
            name='IngredientSearchResponse',
            fields={
                'value':
                CharField(),
                'data':
                inline_serializer(
                    name='IngredientSearchItemResponse',
                    fields={
                        'id': IntegerField(),
                        'name': CharField(),
                        'category': CharField(),
                        'image': CharField(),
                        'image_thumbnail': CharField()
                    }
                )
            }
        )
    },
)
@api_view(['GET'])
def search(request):
    """
    Searches for ingredients.

    This format is currently used by the ingredient search autocompleter
    """
    term = request.GET.get('term', None)
    language_codes = request.GET.get('language', ENGLISH_SHORT_NAME)
    results = []
    json_response = {}

    if not term:
        return Response(json_response)

    languages = [load_language(l) for l in language_codes.split(',')]
    ingredients = Ingredient.objects.filter(
        name__icontains=term,
        language__in=languages,
        status=Ingredient.STATUS_ACCEPTED,
    )[:100]

    for ingredient in ingredients:
        if hasattr(ingredient, 'image'):
            image_obj = ingredient.image
            image = image_obj.image.url
            t = get_thumbnailer(image_obj.image)
            thumbnail = t.get_thumbnail(aliases.get('micro_cropped')).url
        else:
            ingredient.get_image(request)
            image = None
            thumbnail = None

        ingredient_json = {
            'value': ingredient.name,
            'data': {
                'id': ingredient.id,
                'name': ingredient.name,
                'image': image,
                'image_thumbnail': thumbnail
            }
        }
        results.append(ingredient_json)
    json_response['suggestions'] = results

    return Response(json_response)


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for ingredient images
    """
    queryset = Image.objects.all()
    serializer_class = IngredientImageSerializer
    ordering_fields = '__all__'
    filterset_fields = ('uuid', 'ingredient_id', 'ingredient__uuid')

    @method_decorator(cache_page(settings.WGER_SETTINGS['EXERCISE_CACHE_TTL']))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class WeightUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for weight unit objects
    """
    queryset = WeightUnit.objects.all()
    serializer_class = WeightUnitSerializer
    ordering_fields = '__all__'
    filterset_fields = ('language', 'name')


class IngredientWeightUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for many-to-many table ingredient-weight unit objects
    """
    queryset = IngredientWeightUnit.objects.all()
    serializer_class = IngredientWeightUnitSerializer
    ordering_fields = '__all__'
    filterset_fields = (
        'amount',
        'gram',
        'ingredient',
        'unit',
    )


class NutritionPlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for nutrition plan objects. For a read-only endpoint with all
    the information of nutritional plan(s), see /api/v2/nutritionplaninfo/
    """
    serializer_class = NutritionPlanSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'creation_date',
        'language',
        'description',
        'has_goal_calories',
    )

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, "swagger_fake_view", False):
            return NutritionPlan.objects.none()

        return NutritionPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the owner
        """
        serializer.save(user=self.request.user, language=load_language())

    @action(detail=True)
    def nutritional_values(self, request, pk):
        """
        Return an overview of the nutritional plan's values
        """
        return Response(NutritionPlan.objects.get(pk=pk).get_nutritional_values())

    @action(detail=True)
    def get_log_overview(self, request, pk):
        """
        Return a list of log diary entries for the nutrition plan
        """
        plan = get_object_or_404(NutritionPlan, pk=pk, user=request.user)
        return Response(plan.get_log_overview())

    @action(detail=True)
    def log_summary(self, request, pk):
        """
        Return a summary of the nutrition diary for a given date
        """
        today = datetime.date.today()
        year = request.GET.get('year', today.year)
        month = request.GET.get('month', today.month)
        day = request.GET.get('day', today.day)
        plan = get_object_or_404(NutritionPlan, pk=pk, user=request.user)

        try:
            date = datetime.date(year=int(year), month=int(month), day=int(day))
        except ValueError:
            date = today
        return Response(plan.get_log_summary(date))


class NutritionPlanInfoViewSet(NutritionPlanViewSet):
    """
    Read-only info API endpoint for nutrition plan objects. Returns nested data
    structures for more easy parsing.
    """
    serializer_class = NutritionPlanInfoSerializer(read_only=True)


class MealViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for meal objects
    """
    serializer_class = MealSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'order',
        'plan',
        'time',
    )

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, "swagger_fake_view", False):
            return Meal.objects.none()

        return Meal.objects.filter(plan__user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the order
        """
        serializer.save(order=1)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(NutritionPlan, 'plan')]

    @action(detail=True)
    def nutritional_values(self, request, pk):
        """
        Return an overview of the nutritional plan's values
        """
        return Response(Meal.objects.get(pk=pk).get_nutritional_values())


class MealItemViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for meal item objects
    """
    serializer_class = MealItemSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'amount',
        'ingredient',
        'meal',
        'order',
        'weight_unit',
    )

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, "swagger_fake_view", False):
            return MealItem.objects.none()

        return MealItem.objects.filter(meal__plan__user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the order
        """
        serializer.save(order=1)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(Meal, 'meal')]

    @action(detail=True)
    def nutritional_values(self, request, pk):
        """
        Return an overview of the nutritional plan's values
        """
        return Response(MealItem.objects.get(pk=pk).get_nutritional_values())


class LogItemViewSet(WgerOwnerObjectModelViewSet):
    """
    API endpoint for a meal log item
    """

    serializer_class = LogItemSerializer
    is_private = True
    ordering_fields = '__all__'
    filterset_fields = (
        'amount',
        'ingredient',
        'plan',
        'weight_unit',
    )

    def get_queryset(self):
        """
        Only allow access to appropriate objects
        """
        # REST API generation
        if getattr(self, "swagger_fake_view", False):
            return LogItem.objects.none()

        return LogItem.objects.filter(plan__user=self.request.user)

    def get_owner_objects(self):
        """
        Return objects to check for ownership permission
        """
        return [(NutritionPlan, 'plan'), (Meal, 'meal')]

    @action(detail=True)
    def nutritional_values(self, request, pk):
        """
        Return an overview of the nutritional plan's values
        """
        return Response(
            LogItem.objects.get(pk=pk, plan__user=self.request.user).get_nutritional_values()
        )
