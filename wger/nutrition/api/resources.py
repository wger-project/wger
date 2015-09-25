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
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from wger.nutrition.models import (
    Ingredient,
    WeightUnit,
    IngredientWeightUnit,
    NutritionPlan,
    Meal,
    MealItem
)
from wger.utils.resources import UserObjectsOnlyAuthorization
from wger.core.api.resources import LicenseResource, LanguageResource


class IngredientResource(ModelResource):

    language = fields.ToOneField(LanguageResource, 'language')
    license = fields.ToOneField(LicenseResource, 'license')

    class Meta:
        queryset = Ingredient.objects.all()
        filtering = {'id': ALL,
                     'carbohydrates': ALL,
                     'carbohydrates_sugar': ALL,
                     'creation_date': ALL,
                     'energy': ALL,
                     'fat': ALL,
                     'fat_saturated': ALL,
                     'fibres': ALL,
                     'name': ALL,
                     'protein': ALL,
                     'sodium': ALL,
                     'status': ALL,
                     'update_date': ALL,
                     'language': ALL,
                     'license': ALL,
                     'license_author': ALL}


class WeightUnitResource(ModelResource):
    class Meta:
        queryset = WeightUnit.objects.all()
        filtering = {'id': ALL,
                     'name': ALL}


class IngredientToWeightUnit(ModelResource):

    ingredient = fields.ToOneField(IngredientResource, 'ingredient')
    unit = fields.ToOneField(WeightUnitResource, 'unit')

    class Meta:
        queryset = IngredientWeightUnit.objects.all()
        filtering = {'id': ALL,
                     'amount': ALL,
                     'gram': ALL,
                     'ingredient': ALL_WITH_RELATIONS,
                     'unit': ALL_WITH_RELATIONS}


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
        filtering = {'id': ALL,
                     'creation_date': ALL,
                     'description': ALL,
                     'has_goal_calories': ALL}


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
        filtering = {'id': ALL,
                     'order': ALL,
                     'plan': ALL_WITH_RELATIONS,
                     'time': ALL}


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
        filtering = {'id': ALL,
                     'amount': ALL,
                     'ingredient': ALL_WITH_RELATIONS,
                     'meal': ALL_WITH_RELATIONS,
                     'order': ALL,
                     'weight_unit': ALL_WITH_RELATIONS}
