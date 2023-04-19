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

# wger
from wger.celery_configuration import app
from wger.nutrition.sync import (
    download_ingredient_images,
    fetch_ingredient_image,
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
