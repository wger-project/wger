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
from random import (
    choice,
    randint,
)

# Django
from django.conf import settings
from django.core.management import call_command

# Third Party
from celery import shared_task
from celery.schedules import crontab

# wger
from wger.celery_configuration import app
from wger.nutrition.sync import (
    download_ingredient_images,
    fetch_ingredient_image,
    sync_ingredients,
)


logger = logging.getLogger(__name__)


@app.task
def fetch_ingredient_image_task(pk: int):
    """
    Fetches the ingredient image from Open Food Facts servers if it is not available locally

    Returns the image if it is already present in the DB
    """
    fetch_ingredient_image(pk)


@app.task
def fetch_all_ingredient_images_task():
    """
    Fetches the ingredient image from Open Food Facts servers if it is not available locally

    Returns the image if it is already present in the DB
    """
    download_ingredient_images(logger.info)


@shared_task
def sync_all_ingredients_task():
    """
    Fetches the current ingredients from the default wger instance
    """
    sync_ingredients(logger.info)


@app.task
def sync_off_daily_delta():
    """
    Fetches OFF's daily delta product updates
    """
    call_command('import-off-products', '--delta-updates')


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    if settings.WGER_SETTINGS['SYNC_INGREDIENTS_CELERY']:
        sender.add_periodic_task(
            crontab(
                hour=str(randint(0, 23)),
                minute=str(randint(0, 59)),
                day_of_month=str(randint(1, 28)),
                month_of_year=choice(['1, 4, 7, 10', '2, 5, 8, 11', '3, 6, 9, 12']),
            ),
            sync_all_ingredients_task.s(),
            name='Sync ingredients',
        )

    if settings.WGER_SETTINGS['SYNC_OFF_DAILY_DELTA_CELERY']:
        sender.add_periodic_task(
            crontab(
                hour=str(randint(0, 23)),
                minute=str(randint(0, 59)),
            ),
            sync_off_daily_delta.s(),
            name='Sync OFF daily delta updates',
        )
