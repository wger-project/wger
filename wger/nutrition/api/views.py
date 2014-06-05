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
from wger.nutrition.api.serializers import NutritionPlanSerializer

from wger.nutrition.models import Ingredient
from wger.nutrition.models import Meal
from wger.nutrition.models import MealItem
from wger.nutrition.models import WeightUnit
from wger.nutrition.models import IngredientWeightUnit
from wger.nutrition.models import NutritionPlan
from wger.utils.viewsets import WgerOwnerObjectModelViewSet


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for ingredient objects
    '''
    model = Ingredient


class WeightUnitViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for weight unit objects
    '''
    model = WeightUnit


class IngredientWeightUnitViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for many-to-many table ingredient-weight unit objects
    '''
    model = IngredientWeightUnit


class NutritionPlanViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for nutrition plan objects
    '''
    model = NutritionPlan
    serializer_class = NutritionPlanSerializer

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return NutritionPlan.objects.filter(user=self.request.user)

    def pre_save(self, obj):
        '''
        Set the owner
        '''
        obj.user = self.request.user


class MealViewSet(WgerOwnerObjectModelViewSet):
    '''
    API endpoint for meal objects
    '''
    model = Meal

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return NutritionPlan.objects.filter(plan__user=self.request.user)

    def pre_save(self, obj):
        '''
        Set the order
        '''
        obj.order = 1

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [NutritionPlan.objects.get(pk=self.request.DATA['plan'])]


class MealItemViewSet(WgerOwnerObjectModelViewSet):
    '''
    API endpoint for meal item objects
    '''
    model = MealItem

    def get_queryset(self):
        '''
        Only allow access to appropriate objects
        '''
        return MealItem.objects.filter(meal__plan__user=self.request.user)

    def pre_save(self, obj):
        '''
        Set the order
        '''
        obj.order = 1

    def get_owner_objects(self):
        '''
        Return objects to check for ownership permission
        '''
        return [Meal.objects.get(pk=self.request.DATA['meal'])]
