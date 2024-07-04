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
    Image,
    Ingredient,
    IngredientWeightUnit,
    LogItem,
    Meal,
    MealItem,
    NutritionPlan,
    WeightUnit,
)


class IngredientWeightUnitSerializer(serializers.ModelSerializer):
    """
    IngredientWeightUnit serializer
    """

    class Meta:
        model = IngredientWeightUnit
        fields = [
            'id',
            'amount',
            'gram',
            'ingredient',
            'unit',
        ]


class IngredientWeightUnitInfoSerializer(serializers.ModelSerializer):
    """
    IngredientWeightUnit info serializer
    """

    class Meta:
        model = IngredientWeightUnit
        depth = 1
        fields = [
            'gram',
            'amount',
            'unit',
        ]


class WeightUnitSerializer(serializers.ModelSerializer):
    """
    WeightUnit serializer
    """

    class Meta:
        model = WeightUnit
        fields = [
            'id',
            'language',
            'name',
        ]


class IngredientImageSerializer(serializers.ModelSerializer):
    """
    Image serializer
    """

    ingredient_uuid = serializers.CharField(source='ingredient.uuid', read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Image
        fields = [
            'id',
            'uuid',
            'ingredient_id',
            'ingredient_uuid',
            'image',
            'created',
            'last_update',
            'size',
            'width',
            'height',
            'license',
            'license_title',
            'license_object_url',
            'license_author',
            'license_author_url',
            'license_derivative_source_url',
        ]


class IngredientSerializer(serializers.ModelSerializer):
    """
    Ingredient serializer
    """

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'uuid',
            'remote_id',
            'source_name',
            'source_url',
            'code',
            'name',
            'created',
            'last_update',
            'last_imported',
            'energy',
            'protein',
            'carbohydrates',
            'carbohydrates_sugar',
            'fat',
            'fat_saturated',
            'fiber',
            'sodium',
            'license',
            'license_title',
            'license_object_url',
            'license_author',
            'license_author_url',
            'license_derivative_source_url',
            'language',
        ]


class IngredientInfoSerializer(serializers.ModelSerializer):
    """
    Ingredient info serializer
    """

    weight_units = IngredientWeightUnitInfoSerializer(source='ingredientweightunit_set', many=True)
    image = IngredientImageSerializer(read_only=True)

    class Meta:
        model = Ingredient
        depth = 1
        fields = [
            'id',
            'uuid',
            'remote_id',
            'source_name',
            'source_url',
            'code',
            'name',
            'created',
            'last_update',
            'last_imported',
            'energy',
            'protein',
            'carbohydrates',
            'carbohydrates_sugar',
            'fat',
            'fat_saturated',
            'fiber',
            'sodium',
            'weight_units',
            'language',
            'image',
            'license',
            'license_title',
            'license_object_url',
            'license_author',
            'license_author_url',
            'license_derivative_source_url',
        ]


class MealItemSerializer(serializers.ModelSerializer):
    """
    MealItem serializer
    """

    meal = serializers.PrimaryKeyRelatedField(label='Nutrition plan', queryset=Meal.objects.all())

    class Meta:
        model = MealItem
        fields = [
            'id',
            'meal',
            'ingredient',
            'weight_unit',
            'order',
            'amount',
        ]


class LogItemSerializer(serializers.ModelSerializer):
    """
    LogItem serializer
    """

    class Meta:
        model = LogItem
        fields = [
            'id',
            'plan',
            'meal',
            'ingredient',
            'weight_unit',
            'datetime',
            'amount',
        ]


class MealItemInfoSerializer(serializers.ModelSerializer):
    """
    Meal Item info serializer
    """

    meal = serializers.PrimaryKeyRelatedField(read_only=True)
    ingredient = serializers.PrimaryKeyRelatedField(read_only=True)
    ingredient_obj = IngredientInfoSerializer(source='ingredient', read_only=True)
    weight_unit = serializers.PrimaryKeyRelatedField(read_only=True)
    weight_unit_obj = IngredientWeightUnitSerializer(source='weight_unit', read_only=True)
    image = IngredientImageSerializer(source='ingredient.image', read_only=True)

    class Meta:
        model = MealItem
        depth = 1
        fields = [
            'id',
            'meal',
            'ingredient',
            'ingredient_obj',
            'weight_unit',
            'weight_unit_obj',
            'image',
            'order',
            'amount',
        ]


class MealSerializer(serializers.ModelSerializer):
    """
    Meal serializer
    """

    plan = serializers.PrimaryKeyRelatedField(
        label='Nutrition plan',
        queryset=NutritionPlan.objects.all(),
    )

    class Meta:
        model = Meal
        fields = ['id', 'plan', 'order', 'time', 'name']


class NutritionalValuesSerializer(serializers.Serializer):
    """
    Nutritional values serializer
    """

    energy = serializers.FloatField()
    protein = serializers.FloatField()
    carbohydrates = serializers.FloatField()
    carbohydrates_sugar = serializers.FloatField()
    fat = serializers.FloatField()
    fat_saturated = serializers.FloatField()
    fiber = serializers.FloatField()
    sodium = serializers.FloatField()


class MealInfoSerializer(serializers.ModelSerializer):
    """
    Meal info serializer
    """

    meal_items = MealItemInfoSerializer(source='mealitem_set', many=True)
    plan = serializers.PrimaryKeyRelatedField(read_only=True)
    nutritional_values = NutritionalValuesSerializer(
        source='get_nutritional_values',
        read_only=True,
    )

    class Meta:
        model = Meal
        fields = [
            'id',
            'plan',
            'order',
            'time',
            'name',
            'meal_items',
            'nutritional_values',
        ]


class NutritionPlanSerializer(serializers.ModelSerializer):
    """
    Nutritional plan serializer
    """

    # nutritional_values = NutritionalValuesSerializer(source='get_nutritional_values.total')

    class Meta:
        model = NutritionPlan
        fields = [
            'id',
            'creation_date',
            'description',
            'only_logging',
            'goal_energy',
            'goal_protein',
            'goal_carbohydrates',
            'goal_fat',
            'goal_fiber',
            # 'nutritional_values',
        ]


class NutritionPlanInfoSerializer(serializers.ModelSerializer):
    """
    Nutritional plan info serializer
    """

    meals = MealInfoSerializer(source='meal_set', many=True)

    class Meta:
        model = NutritionPlan
        depth = 1
        fields = [
            'id',
            'creation_date',
            'description',
            'only_logging',
            'goal_energy',
            'goal_protein',
            'goal_carbohydrates',
            'goal_fat',
            'goal_fiber',
            'meals',
        ]
