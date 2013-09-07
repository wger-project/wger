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
from tastypie.authentication import ApiKeyAuthentication
from tastypie.resources import ModelResource

from wger.nutrition.models import Ingredient
from wger.nutrition.models import WeightUnit
from wger.nutrition.models import IngredientWeightUnit
from wger.nutrition.models import NutritionPlan
from wger.nutrition.models import Meal
from wger.nutrition.models import MealItem
from wger.utils.resources import UserObjectsOnlyAuthorization


class IngredientResource(ModelResource):
    class Meta:
        queryset = Ingredient.objects.all()


class WeightUnitResource(ModelResource):
    class Meta:
        queryset = WeightUnit.objects.all()


class IngredientToWeightUnit(ModelResource):

    ingredient = fields.ToOneField(IngredientResource, 'ingredient')
    unit = fields.ToOneField(WeightUnitResource, 'unit')

    class Meta:
        queryset = IngredientWeightUnit.objects.all()


class NutritionPlanResource(ModelResource):
    '''
    Resource for nutritional plans
    '''

    meals = fields.ToManyField('wger.nutrition.api.resources.MealResource', 'meal_set')

    def authorized_read_list(self, object_list, bundle):
        '''
        Filter to own objects
        '''
        return object_list.filter(user=bundle.request.user)

    def dehydrate(self, bundle):
        '''
        Also send the nutritional values
        '''
        bundle.data['nutritional_values'] = bundle.obj.get_nutritional_values()
        return bundle

    class Meta:
        queryset = NutritionPlan.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()


class MealResource(ModelResource):
    '''
    Resource for meals
    '''

    plan = fields.ToOneField(NutritionPlanResource, 'plan')
    meal_items = fields.ToManyField('wger.nutrition.api.resources.MealItemResource', 'mealitem_set')

    def authorized_read_list(self, object_list, bundle):
        '''
        Filter to own objects
        '''
        return object_list.filter(plan__user=bundle.request.user)

    def dehydrate(self, bundle):
        '''
        Also send the nutritional values
        '''
        bundle.data['nutritional_values'] = bundle.obj.get_nutritional_values()
        return bundle

    class Meta:
        queryset = Meal.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()


class MealItemResource(ModelResource):
    '''
    Resource for meal items
    '''

    meal = fields.ToOneField(MealResource, 'meal')
    ingredient = fields.ToOneField(IngredientResource, 'ingredient')
    weight_unit = fields.ToOneField(WeightUnitResource, 'weight_unit', null=True)

    def authorized_read_list(self, object_list, bundle):
        '''
        Filter to own objects
        '''
        return object_list.filter(meal__plan__user=bundle.request.user)

    def dehydrate(self, bundle):
        '''
        Also send the nutritional values
        '''
        bundle.data['nutritional_values'] = bundle.obj.get_nutritional_values()
        return bundle

    class Meta:
        queryset = MealItem.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
