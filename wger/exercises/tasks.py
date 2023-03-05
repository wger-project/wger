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

# Third Party
from celery.schedules import crontab

# wger
from wger.celery_configuration import app
from wger.exercises.sync import (
    delete_entries,
    sync_categories,
    sync_equipment,
    sync_exercises,
    sync_languages,
    sync_muscles,
)


logger = logging.getLogger(__name__)


@app.task
def sync_exercises_task():
    """
    Fetches the current exercises from the default wger instance
    """
    sync_languages(logger.info)
    sync_categories(logger.info)
    sync_muscles(logger.info)
    sync_equipment(logger.info)
    sync_exercises(logger.info)
    sync_exercises(logger.info)
    delete_entries(logger.info)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=10, minute=30, day_of_week='monday'),
        sync_exercises_task.s(),
        name='Regularly sync exercises',
    )
