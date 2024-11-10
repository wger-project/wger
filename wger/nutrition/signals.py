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

# Standard Library
import pathlib

# Django
from django.core.cache import cache
from django.db.models.signals import (
    post_delete,
    post_save,
)

# wger
from wger.nutrition.models import (
    Image,
    Meal,
    MealItem,
    NutritionPlan,
)
from wger.utils.cache import cache_mapper


def reset_nutritional_values_canonical_form(sender, instance, **kwargs):
    """
    Reset the nutrition values canonical form in cache
    """
    cache.delete(cache_mapper.get_nutrition_cache_by_key(instance.get_owner_object().id))


post_save.connect(reset_nutritional_values_canonical_form, sender=NutritionPlan)
post_delete.connect(reset_nutritional_values_canonical_form, sender=NutritionPlan)
post_save.connect(reset_nutritional_values_canonical_form, sender=Meal)
post_delete.connect(reset_nutritional_values_canonical_form, sender=Meal)
post_save.connect(reset_nutritional_values_canonical_form, sender=MealItem)
post_delete.connect(reset_nutritional_values_canonical_form, sender=MealItem)


def auto_delete_file_on_delete(sender, instance: Image, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if not instance.image:
        return

    path = pathlib.Path(instance.image.path)
    if path.exists():
        path.unlink()


post_delete.connect(auto_delete_file_on_delete, sender=Image)
