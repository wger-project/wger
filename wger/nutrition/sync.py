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
from openfoodfacts.images import (
    AWS_S3_BASE_URL,
    generate_image_path,
)

# wger
from wger.nutrition.api.endpoints import (
    IMAGE_ENDPOINT,
    INGREDIENTS_ENDPOINT,
)
from wger.nutrition.models import (
    Image,
    Ingredient,
    Source,
)
from wger.utils.constants import (
    API_MAX_ITEMS,
    CC_BY_SA_3_LICENSE_ID,
    DOWNLOAD_INGREDIENT_OFF,
    DOWNLOAD_INGREDIENT_WGER,
)
from wger.utils.requests import (
    get_paginated,
    wger_headers,
)
from wger.utils.url import make_uri


logger = logging.getLogger(__name__)


def fetch_ingredient_image(pk: int):
    # wger
    from wger.nutrition.models import Ingredient

    try:
        ingredient = Ingredient.objects.get(pk=pk)
    except Ingredient.DoesNotExist:
        logger.info(f'Ingredient with ID {pk} does not exist')
        return

    if hasattr(ingredient, 'image'):
        return

    if ingredient.source_name != Source.OPEN_FOOD_FACTS.value:
        return

    if not ingredient.source_url:
        return

    if settings.TESTING:
        return

    logger.info(f'Fetching image for ingredient {pk}')
    if settings.WGER_SETTINGS['DOWNLOAD_INGREDIENTS_FROM'] == DOWNLOAD_INGREDIENT_OFF:
        fetch_image_from_off(ingredient)
    elif settings.WGER_SETTINGS['DOWNLOAD_INGREDIENTS_FROM'] == DOWNLOAD_INGREDIENT_WGER:
        fetch_image_from_wger_instance(ingredient)


def fetch_image_from_wger_instance(ingredient):
    url = make_uri(IMAGE_ENDPOINT, query={'ingredient__uuid': ingredient.uuid})
    logger.info(f'Trying to fetch image from WGER for {ingredient.name} (UUID: {ingredient.uuid})')
    result = requests.get(url, headers=wger_headers()).json()
    if result['count'] == 0:
        logger.info('No ingredient matches UUID in the remote server')

    image_data = result['results'][0]
    image_uuid = image_data['uuid']
    try:
        Image.objects.get(uuid=image_uuid)
        logger.info('image already present locally, skipping...')
        return
    except Image.DoesNotExist:
        retrieved_image = requests.get(image_data['image'], headers=wger_headers())
        Image.from_json(ingredient, retrieved_image, image_data)


def fetch_image_from_off(ingredient: Ingredient):
    """
    See
    - https://openfoodfacts.github.io/openfoodfacts-server/api/how-to-download-images/
    - https://openfoodfacts.github.io/openfoodfacts-server/api/ref-v2/
    """
    logger.info(f'Trying to fetch image from OFF for {ingredient.name} (UUID: {ingredient.uuid})')

    url = ingredient.source_url + '?fields=images,image_front_url'
    headers = wger_headers()
    try:
        product_data = requests.get(url, headers=headers, timeout=3).json()
    except requests.JSONDecodeError:
        logger.warning(f'Could not decode JSON response from {url}')
        return
    except requests.ConnectTimeout as e:
        logger.warning(f'Connection timeout while trying to fetch {url}: {e}')
        return
    except requests.ReadTimeout as e:
        logger.warning(f'Read timeout while trying to fetch {url}: {e}')
        return

    try:
        image_url: Optional[str] = product_data['product'].get('image_front_url')
    except KeyError:
        logger.info('No "product" key found, exiting...')
        return

    if not image_url:
        logger.info('Product data has no "image_front_url" key')
        return
    image_data = product_data['product']['images']

    # Extract the image key from the url:
    # https://images.openfoodfacts.org/images/products/00975957/front_en.5.400.jpg -> "front_en"
    image_id: str = image_url.rpartition('/')[2].partition('.')[0]

    # Extract the uploader name
    try:
        image_id: str = image_data[image_id]['imgid']
        uploader_name: str = image_data[image_id]['uploader']
    except KeyError as e:
        logger.info('could not load all image information, skipping...', e)
        return

    # Download image from amazon
    image_s3_url = f'{AWS_S3_BASE_URL}{generate_image_path(ingredient.code, image_id)}'
    response = requests.get(image_s3_url, headers=headers)
    if not response.ok:
        logger.info(f'Could not locate image on AWS! Status code: {response.status_code}')
        return

    # Save to DB
    url = (
        f'https://world.openfoodfacts.org/cgi/product_image.pl?code={ingredient.code}&id={image_id}'
    )
    uploader_url = f'https://world.openfoodfacts.org/photographer/{uploader_name}'
    image_data = {
        'image': os.path.basename(image_url),
        'license': CC_BY_SA_3_LICENSE_ID,
        'license_title': 'Photo',
        'license_author': uploader_name,
        'license_author_url': uploader_url,
        'license_object_url': url,
        'license_derivative_source_url': '',
        'size': len(response.content),
    }
    try:
        Image.from_json(ingredient, response, image_data, generate_uuid=True)
    # Due to a race condition (e.g. when adding tasks over the search), we might
    # try to save an image to an ingredient that already has one. In that case,
    # just ignore the error
    except IntegrityError:
        logger.info('Ingredient has already an image, skipping...')
        return
    logger.info('Image successfully saved')


def download_ingredient_images(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    headers = wger_headers()
    url = make_uri(IMAGE_ENDPOINT, server_url=remote_url, query={'limit': 100})

    print_fn('*** Processing ingredient images ***')
    for image_data in get_paginated(url, headers=headers):
        image_uuid = image_data['uuid']
        print_fn(f'Processing image {image_uuid}')

        try:
            ingredient = Ingredient.objects.get(uuid=image_data['ingredient_uuid'])
        except Ingredient.DoesNotExist:
            print_fn('    Remote ingredient not found in local DB, skipping...')
            continue

        if hasattr(ingredient, 'image'):
            continue

        try:
            Image.objects.get(uuid=image_uuid)
            print_fn('    Image already present locally, skipping...')
            continue
        except Image.DoesNotExist:
            print_fn('    Image not found in local DB, creating now...')
            retrieved_image = requests.get(image_data['image'], headers=headers)
            Image.from_json(ingredient, retrieved_image, image_data)

        print_fn(style_fn('    successfully saved'))


def sync_ingredients(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Synchronize the ingredients from the remote server"""
    print_fn('*** Synchronizing ingredients...')

    url = make_uri(INGREDIENTS_ENDPOINT, server_url=remote_url, query={'limit': API_MAX_ITEMS})
    for data in get_paginated(url, headers=wger_headers()):
        uuid = data['uuid']
        name = data['name']

        ingredient, created = Ingredient.objects.update_or_create(
            uuid=uuid,
            defaults={
                'name': name,
                'code': data['code'],
                'language_id': data['language'],
                'created': data['created'],
                'license_id': data['license'],
                'license_object_url': data['license_object_url'],
                'license_author': data['license_author_url'],
                'license_author_url': data['license_author_url'],
                'license_title': data['license_title'],
                'license_derivative_source_url': data['license_derivative_source_url'],
                'energy': data['energy'],
                'carbohydrates': data['carbohydrates'],
                'carbohydrates_sugar': data['carbohydrates_sugar'],
                'fat': data['fat'],
                'fat_saturated': data['fat_saturated'],
                'protein': data['protein'],
                'fiber': data['fiber'],
                'sodium': data['sodium'],
            },
        )

        print_fn(f'{"created" if created else "updated"} ingredient {uuid} - {name}')

    print_fn(style_fn('done!\n'))
