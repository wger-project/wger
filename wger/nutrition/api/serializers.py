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

# Third Party
from rest_framework import serializers

# wger
from wger.nutrition.models import (
    Ingredient,
    IngredientWeightUnit,
    Meal,
    MealItem,
    NutritionPlan,
    WeightUnit
)


class NutritionPlanSerializer(serializers.ModelSerializer):
    '''
    Nutritional plan serializer
    '''

    class Meta:
        model = NutritionPlan
        exclude = ('user',)


class IngredientWeightUnitSerializer(serializers.ModelSerializer):
    '''
    IngredientWeightUnit serializer
    '''

    class Meta:
        model = IngredientWeightUnit
        fields = '__all__'


class WeightUnitSerializer(serializers.ModelSerializer):
    '''
    WeightUnit serializer
    '''

    class Meta:
        model = WeightUnit
        fields = '__all__'


class MealItemSerializer(serializers.ModelSerializer):
    '''
    MealItem serializer
    '''
    meal = serializers.PrimaryKeyRelatedField(label='Nutrition plan',
                                              queryset=Meal.objects.all())

    class Meta:
        model = MealItem
        fields = '__all__'


class MealSerializer(serializers.ModelSerializer):
    '''
    Meal serializer
    '''
    plan = serializers.PrimaryKeyRelatedField(label='Nutrition plan',
                                              queryset=NutritionPlan.objects.all())

    class Meta:
        model = Meal
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Ingredient serializer
    '''

    class Meta:
        model = Ingredient
        fields = '__all__'
