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
from rest_framework.decorators import detail_route
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wger.nutrition.api.serializers import (
    NutritionPlanSerializer,
    IngredientWeightUnitSerializer,
    WeightUnitSerializer,
    MealItemSerializer,
    MealSerializer,
    IngredientSerializer
)
from wger.nutrition.forms import UnitChooserForm
from wger.nutrition.models import (
    Ingredient,
    Meal,
    MealItem,
    WeightUnit,
    IngredientWeightUnit,
    NutritionPlan
)
from wger.utils.language import load_ingredient_languages, load_language
from wger.utils.viewsets import WgerOwnerObjectModelViewSet


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for ingredient objects
    '''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    ordering_fields = '__all__'
    filter_fields = ('carbohydrates',
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
                     'user',
                     'license',
                     'license_author')

    @detail_route()
    def get_values(self, request, pk):
        '''
        Calculates the nutritional values for current ingredient and
        the given amount and unit.

        This function basically just performs a multiplication (in the model), and
        is a candidate to be moved to pure AJAX calls, however doing it like this
        keeps the logic nicely hidden and respects the DRY principle.
        '''

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


@api_view(['GET'])
def search(request):
    '''
    Searches for ingredients.

    This format is currently used by the ingredient search autocompleter
    '''
    q = request.GET.get('term', None)
    results = []
    json_response = {}
    if q:
        languages = load_ingredient_languages(request)
        ingredients = Ingredient.objects.filter(name__icontains=q,
                                                language__in=languages,
                                                status__in=Ingredient.INGREDIENT_STATUS_OK)

        for ingredient in ingredients:
            ingredient_json = {
                'value': ingredient.name,
                'data': {
                    'id': ingredient.id,
                    'name': ingredient.name,
                }
            }
            results.append(ingredient_json)
        json_response['suggestions'] = results

    return Response(json_response)


class WeightUnitViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for weight unit objects
    '''
    queryset = WeightUnit.objects.all()
    serializer_class = WeightUnitSerializer
    ordering_fields = '__all__'
    filter_fields = ('language',
                     'name')


class IngredientWeightUnitViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for many-to-many table ingredient-weight unit objects
    '''
    queryset = IngredientWeightUnit.objects.all()
    serializer_class = IngredientWeightUnitSerializer
    ordering_fields = '__all__'
    filter_fields = ('amount',
                     'gram',
                     'ingredient',
                     'unit')


class NutritionPlanViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for nutrition plan objects
    '''
    serializer_class = NutritionPlanSerializer
    is_private = True
    ordering_fields = '__all__'
    filter_fields = ('creation_date',
                     'language',
                     'description',
                     'has_goal_calories')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return NutritionPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        '''
        Set the owner
        '''
        serializer.save(user=self.request.user, language=load_language())

    @detail_route()
    def nutritional_values(self, request, pk):
        '''
        Return an overview of the nutritional plan's values
        '''
        return Response(NutritionPlan.objects.get(pk=pk).get_nutritional_values())


class MealViewSet(WgerOwnerObjectModelViewSet):
    '''
    API endpoint for meal objects
    '''
    serializer_class = MealSerializer
    is_private = True
    ordering_fields = '__all__'
    filter_fields = ('order',
                     'plan',
                     'time')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return Meal.objects.filter(plan__user=self.request.user)

    def perform_create(self, serializer):
        '''
        Set the order
        '''
        serializer.save(order=1)

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [(NutritionPlan, 'plan')]

    @detail_route()
    def nutritional_values(self, request, pk):
        '''
        Return an overview of the nutritional plan's values
        '''
        return Response(Meal.objects.get(pk=pk).get_nutritional_values())


class MealItemViewSet(WgerOwnerObjectModelViewSet):
    '''
    API endpoint for meal item objects
    '''
    serializer_class = MealItemSerializer
    is_private = True
    ordering_fields = '__all__'
    filter_fields = ('amount',
                     'ingredient',
                     'meal',
                     'order',
                     'weight_unit')

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return MealItem.objects.filter(meal__plan__user=self.request.user)

    def perform_create(self, serializer):
        '''
        Set the order
        '''
        serializer.save(order=1)

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [(Meal, 'meal')]

    @detail_route()
    def nutritional_values(self, request, pk):
        '''
        Return an overview of the nutritional plan's values
        '''
        return Response(MealItem.objects.get(pk=pk).get_nutritional_values())
