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
    LogItem,
    Meal,
    MealItem,
    NutritionPlan,
    WeightUnit
)


class IngredientWeightUnitSerializer(serializers.ModelSerializer):
    """
    IngredientWeightUnit serializer
    """

    class Meta:
        model = IngredientWeightUnit
        fields = ['id',
                  'amount',
                  'gram',
                  'ingredient',
                  'unit']


class IngredientWeightUnitInfoSerializer(serializers.ModelSerializer):
    """
    IngredientWeightUnit info serializer
    """

    class Meta:
        model = IngredientWeightUnit
        depth = 1
        fields = ['gram',
                  'amount',
                  'unit']


class WeightUnitSerializer(serializers.ModelSerializer):
    """
    WeightUnit serializer
    """

    class Meta:
        model = WeightUnit
        fields = ['language',
                  'name']


class IngredientSerializer(serializers.ModelSerializer):
    """
    Ingredient serializer
    """

    class Meta:
        model = Ingredient
        fields = ['id',
                  'name',
                  'creation_date',
                  'update_date',
                  'energy',
                  'protein',
                  'carbohydrates',
                  'carbohydrates_sugar',
                  'fat',
                  'fat_saturated',
                  'fibres',
                  'sodium',
                  'license',
                  'license_author',
                  'language']


class IngredientInfoSerializer(serializers.ModelSerializer):
    """
    Ingredient info serializer
    """

    ingredientweightunit_set = IngredientWeightUnitInfoSerializer(many=True)

    class Meta:
        model = Ingredient
        depth = 1
        fields = ['id',
                  'name',
                  'creation_date',
                  'update_date',
                  'energy',
                  'protein',
                  'carbohydrates',
                  'carbohydrates_sugar',
                  'fat',
                  'fat_saturated',
                  'fibres',
                  'sodium',
                  'license',
                  'license_author',
                  'ingredientweightunit_set',
                  'language']


class MealItemSerializer(serializers.ModelSerializer):
    """
    MealItem serializer
    """
    meal = serializers.PrimaryKeyRelatedField(label='Nutrition plan',
                                              queryset=Meal.objects.all())

    class Meta:
        model = MealItem
        fields = ['id',
                  'meal',
                  'ingredient',
                  'weight_unit',
                  'order',
                  'amount']


class LogItemSerializer(serializers.ModelSerializer):
    """
    LogItem serializer
    """

    class Meta:
        model = LogItem
        fields = ['id',
                  'plan',
                  'ingredient',
                  'weight_unit',
                  'datetime',
                  'amount']


class MealItemInfoSerializer(serializers.ModelSerializer):
    """
    Meal Item info serializer
    """

    meal = serializers.PrimaryKeyRelatedField(read_only=True)
    ingredient = serializers.PrimaryKeyRelatedField(read_only=True)
    ingredient_obj = IngredientInfoSerializer(source='ingredient', read_only=True)

    class Meta:
        model = MealItem
        depth = 1
        fields = ['id',
                  'meal',
                  'ingredient_obj',
                  'ingredient',
                  'weight_unit',
                  'order',
                  'amount']


class MealSerializer(serializers.ModelSerializer):
    """
    Meal serializer
    """
    plan = serializers.PrimaryKeyRelatedField(label='Nutrition plan',
                                              queryset=NutritionPlan.objects.all())

    class Meta:
        model = Meal
        fields = ['id',
                  'plan',
                  'order',
                  'time']


class MealInfoSerializer(serializers.ModelSerializer):
    """
    Meal info serializer
    """

    meal_items = MealItemInfoSerializer(source='mealitem_set', many=True)
    plan = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Meal
        fields = ['id',
                  'plan',
                  'order',
                  'time',
                  'meal_items',
                  'get_nutritional_values']


class NutritionPlanSerializer(serializers.ModelSerializer):
    """
    Nutritional plan serializer
    """

    class Meta:
        model = NutritionPlan
        exclude = ('user',)


class NutritionPlanInfoSerializer(serializers.ModelSerializer):
    """
    Nutritional plan info serializer
    """

    meals = MealInfoSerializer(source='meal_set', many=True)

    class Meta:
        model = NutritionPlan
        depth = 1
        fields = ['id',
                  'language',
                  'creation_date',
                  'description',
                  'get_nutritional_values',
                  'meals']
