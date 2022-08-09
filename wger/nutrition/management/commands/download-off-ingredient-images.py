# -*- coding: utf-8 *-*

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
import datetime

# Django
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.management.base import BaseCommand
from django.template import loader
from django.utils import translation
from django.utils.translation import gettext_lazy as _

# wger
from wger.nutrition.models import MealItem


class Command(BaseCommand):
    """
    Download images of all Open Food Facts ingredients that are used in a nutrition plan
    """

    help = 'Download images of all Open Food Facts ingredients that are used in a nutrition plan'

    def handle(self, **options):
        # Make sure off downloads are enabled
        settings.WGER_SETTINGS['DOWNLOAD_FROM_OFF'] = True

        # Since each MealItem is linked to a NutritionPlan via a Meal we can skip accessing
        # NutritionPlan and Meal itself and fetch all MealItems directly instead.
        meal_items = MealItem.objects.all()
        meal_item_counter = 0
        download_counter = 0
        for meal_item in meal_items:
            if meal_item.ingredient.fetch_image():
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
