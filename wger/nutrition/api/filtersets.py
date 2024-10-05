# Third Party
from django_filters import rest_framework as filters

# wger
from wger.nutrition.models import (
    Ingredient,
    LogItem,
)


class LogItemFilterSet(filters.FilterSet):
    class Meta:
        model = LogItem
        fields = {
            'datetime': ['exact', 'date'],
            'amount': ['exact'],
            'ingredient': ['exact'],
            'plan': ['exact'],
            'weight_unit': ['exact'],
        }


class IngredientFilterSet(filters.FilterSet):
    class Meta:
        model = Ingredient
        fields = {
            'id': ['exact', 'in'],
            'uuid': ['exact'],
            'code': ['exact'],
            'source_name': ['exact'],
            'name': ['exact'],
            'energy': ['exact'],
            'protein': ['exact'],
            'carbohydrates': ['exact'],
            'carbohydrates_sugar': ['exact'],
            'fat': ['exact'],
            'fat_saturated': ['exact'],
            'fiber': ['exact'],
            'sodium': ['exact'],
            'created': ['exact', 'gt', 'lt'],
            'last_update': ['exact', 'gt', 'lt'],
            'last_imported': ['exact', 'gt', 'lt'],
            'language': ['exact'],
            'license': ['exact'],
            'license_author': ['exact'],
        }
