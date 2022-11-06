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
import os
from typing import Optional

# Django
from django.conf import settings
from django.db import IntegrityError

# Third Party
import requests
from celery import shared_task
from requests.utils import default_user_agent

# wger
from wger import get_version
from wger.nutrition.models import Image
from wger.nutrition.models.sources import Source


logger = logging.getLogger(__name__)


@shared_task()
def fetch_ingredient_image(pk: int):
    """
    Fetches the ingredient image from Open Food Facts servers if it is not available locally

    Returns the image if it was fetched
    """
    # wger
    from wger.nutrition.models import Ingredient
    ingredient = Ingredient.objects.get(pk=pk)

    if hasattr(ingredient, 'image'):
        return

    if ingredient.source_name != Source.OPEN_FOOD_FACTS.value:
        return

    if not settings.WGER_SETTINGS['DOWNLOAD_FROM_OFF']:
        return

    if settings.TESTING:
        return

    # Everything looks fine, go ahead
    logger.info(f'Trying to fetch image from OFF for {ingredient.name} (UUID: {ingredient.uuid})')
    headers = {
        'User-agent': default_user_agent(f'wger/{get_version()} - https://github.com/wger-project')
    }

    # Fetch the product data
    product_data = requests.get(ingredient.source_url, headers=headers).json()
    image_url: Optional[str] = product_data['product'].get('image_front_url')
    if not image_url:
        return

    image_data = product_data['product']['images']

    # Download the image file
    response = requests.get(image_url, headers=headers)
    if response.status_code != 200:
        logger.info('An error occurred!')
        return

    # Parse the file name, looks something like this:
    # https://images.openfoodfacts.org/images/products/00975957/front_en.5.400.jpg
    image_name: str = image_url.rpartition("/")[2].partition(".")[0]

    # Retrieve the uploader name
    try:
        image_id: str = image_data[image_name]['imgid']
        uploader_name: str = image_data[image_id]['uploader']
    except KeyError:
        return

    # Save to DB
    image_data: dict = {
        'image': os.path.basename(image_url),
        'license_author': uploader_name,
        'size': len(response.content)
    }
    try:
        Image.from_json(ingredient, response, image_data, headers, generate_uuid=True)
    # Due to a race condition (e.g. when adding tasks over the search), we might
    # try to save an image to an ingredient that already has one. In that case,
    # just ignore the error
    except IntegrityError:
        logger.info('Ingredient has already an image, skipping...')
        return
    logger.info('Image successfully saved')
