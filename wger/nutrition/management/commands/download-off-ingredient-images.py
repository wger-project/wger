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
import logging

# Django
from django.conf import settings
from django.core.management.base import BaseCommand

# wger
from wger.nutrition.models import MealItem
from wger.nutrition.tasks import fetch_ingredient_image_task


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    One off script

    This is intended to download all images from Open Food Facts for the all
    currently used ingredients
    """

    help = 'Download images of all Open Food Facts ingredients that are used in a nutritional plan'

    def handle(self, **options):
        if not settings.WGER_SETTINGS['USE_CELERY']:
            self.stdout.write('Celery deactivated. Exiting...')
            return

        # Make sure off downloads are enabled
        if not settings.WGER_SETTINGS['DOWNLOAD_INGREDIENTS_FROM']:
            self.stdout.write('DOWNLOAD_INGREDIENTS_FROM not set. Exiting...')
            return

        # Since each MealItem is linked to a NutritionPlan via a Meal we can skip accessing
        # NutritionPlan and Meal itself and fetch all MealItems directly instead.
        meal_items = MealItem.objects.all()
        meal_item_counter = 0
        download_counter = 0
        for meal_item in meal_items:
            if meal_item.ingredient:
                fetch_ingredient_image_task.delay(meal_item.ingredient.pk)
                download_counter += 1
            meal_item_counter += 1

            if meal_item_counter % 10 == 0:
                self.stdout.write(
                    f'Processed {meal_item_counter} meal items, '
                    f'downloaded {download_counter} images'
                )

        self.stdout.write(
            f'Processed {meal_item_counter} meal items, downloaded {download_counter} images'
        )
        self.stdout.write(f'Done')
