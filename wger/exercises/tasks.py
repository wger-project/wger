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
import random

# Django
from django.conf import settings

# Third Party
from celery.schedules import crontab

# wger
from wger.celery_configuration import app
from wger.exercises.sync import (
    download_exercise_images,
    download_exercise_videos,
    handle_deleted_entries,
    sync_categories,
    sync_equipment,
    sync_exercises,
    sync_languages,
    sync_licenses,
    sync_muscles,
)


logger = logging.getLogger(__name__)


@app.task
def sync_exercises_task():
    """
    Fetches the current exercises from the default wger instance
    """
    sync_languages(logger.info)
    sync_licenses(logger.info)
    sync_categories(logger.info)
    sync_muscles(logger.info)
    sync_equipment(logger.info)
    sync_exercises(logger.info)
    handle_deleted_entries(logger.info)


@app.task
def sync_images_task():
    """
    Fetches the exercise images from the default wger instance
    """
    download_exercise_images(logger.info)


@app.task
def sync_videos_task():
    """
    Fetches the exercise videos from the default wger instance
    """
    download_exercise_videos(logger.info)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    if settings.WGER_SETTINGS['SYNC_EXERCISES_CELERY']:
        sender.add_periodic_task(
            crontab(
                hour=str(random.randint(0, 23)),
                minute=str(random.randint(0, 59)),
                day_of_week=str(random.randint(0, 6)),
            ),
            sync_exercises_task.s(),
            name='Sync exercises',
        )

    if settings.WGER_SETTINGS['SYNC_EXERCISE_IMAGES_CELERY']:
        sender.add_periodic_task(
            crontab(
                hour=str(random.randint(0, 23)),
                minute=str(random.randint(0, 59)),
                day_of_week=str(random.randint(0, 6)),
            ),
            sync_images_task.s(),
            name='Sync exercise images',
        )

    if settings.WGER_SETTINGS['SYNC_EXERCISE_VIDEOS_CELERY']:
        sender.add_periodic_task(
            crontab(
                hour=str(random.randint(0, 23)),
                minute=str(random.randint(0, 59)),
                day_of_week=str(random.randint(0, 6)),
            ),
            sync_videos_task.s(),
            name='Sync exercise videos',
        )
