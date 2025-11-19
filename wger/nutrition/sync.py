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
from typing import (
    List,
    Optional,
)

# Django
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone

# Third Party
import requests
from openfoodfacts import (
    API,
    APIVersion,
    Country,
    Environment,
    Flavor,
)
from openfoodfacts.images import download_image
from tqdm import tqdm

# wger
from wger.core.models.language import Language
from wger.nutrition.api.endpoints import (
    IMAGE_ENDPOINT,
    INGREDIENTS_ENDPOINT,
)
from wger.nutrition.extract_info.wger import extract_info_from_wger_api
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
from wger.utils.language import load_language
from wger.utils.requests import (
    get_paginated,
    wger_headers,
    wger_user_agent,
)
from wger.utils.url import make_uri


logger = logging.getLogger(__name__)


def fetch_ingredient_image(pk: int):
    # wger
    from wger.nutrition.models import Ingredient

    try:
        ingredient = Ingredient.objects.get(pk=pk)
    except Ingredient.DoesNotExist:
        logger.debug(f'Ingredient with ID {pk} does not exist')
        return

    if hasattr(ingredient, 'image'):
        # logger.debug(f'Ingredient {pk} already has an image, skipping...')
        return

    if not ingredient.source_url:
        # logger.debug(f'Ingredient {pk} does not have a source URL, skipping...')
        return

    if (
        ingredient.last_image_check
        and (
            ingredient.last_image_check + settings.WGER_SETTINGS['INGREDIENT_IMAGE_CHECK_INTERVAL']
        )
        > timezone.now()
    ):
        # logger.debug(
        #     f'Last image check for ingredient {pk} is too recent'
        #     f' ({ingredient.last_image_check}), skipping...')
        return

    if settings.TESTING:
        return

    logger.info(f'Fetching image for ingredient {pk}')
    if settings.WGER_SETTINGS['DOWNLOAD_INGREDIENTS_FROM'] == DOWNLOAD_INGREDIENT_OFF:
        if ingredient.source_name != Source.OPEN_FOOD_FACTS.value:
            # logger.debug(f'Ingredient {pk} is not from Open Food Facts, skipping...')
            return

        fetch_image_from_off(ingredient)
    elif settings.WGER_SETTINGS['DOWNLOAD_INGREDIENTS_FROM'] == DOWNLOAD_INGREDIENT_WGER:
        fetch_image_from_wger_instance(ingredient)
    else:
        logger.info('No image backend configured, skipping...')


def fetch_image_from_wger_instance(ingredient):
    url = make_uri(IMAGE_ENDPOINT, query={'ingredient__uuid': ingredient.uuid})
    logger.info(f'Trying to fetch image from WGER for {ingredient.name} (UUID: {ingredient.uuid})')
    result = requests.get(url, headers=wger_headers()).json()
    if result['count'] == 0:
        logger.info('No image for ingredient found in the remote server')
        return

    image_data = result['results'][0]
    image_uuid = image_data['uuid']
    try:
        Image.objects.get(uuid=image_uuid)
        logger.info('image already present locally, skipping...')
        return
    except Image.DoesNotExist:
        retrieved_image = requests.get(image_data['image'], headers=wger_headers())
        image = Image.from_json(ingredient, retrieved_image, image_data)
        image.ingredient.last_image_check = timezone.now()
        image.ingredient.save()


def fetch_image_from_off(ingredient: Ingredient):
    """
    See
    - https://openfoodfacts.github.io/openfoodfacts-server/api/how-to-download-images/
    - https://openfoodfacts.github.io/openfoodfacts-server/api/ref-v2/
    """
    logger.info(f'Trying to fetch image from OFF for "{ingredient.name}" ({ingredient.uuid})')
    off_api = API(
        user_agent=wger_user_agent(),
        country=Country.world,
        flavor=Flavor.off,
        version=APIVersion.v2,
        environment=Environment.org,
    )
    product_data = off_api.product.get(ingredient.code, fields=['images', 'image_front_url'])

    if product_data is None:
        logger.info('No product data found for this ingredient')
        return

    image_url: Optional[str] = product_data.get('image_front_url')
    if not image_url:
        logger.info('Product data has no "image_front_url" key')
        return
    image_data = product_data['images']
    if not image_data:
        logger.info('Product data has no "images" key')
        return

    # Extract the image key from the url:
    # https://images.openfoodfacts.org/images/products/00975957/front_en.5.400.jpg -> "front_en"
    image_key: str = image_url.rpartition('/')[2].partition('.')[0]

    # Extract the uploader name and numerical image id
    try:
        image_id: str = image_data[image_key]['imgid']
        uploader_name: str = image_data[image_id]['uploader']
    except KeyError as e:
        logger.info('could not load all image information, skipping...', e)
        return

    off_response = download_image(image_url, return_struct=True)

    # Save to DB
    url = make_uri(
        'https://world.openfoodfacts.org/cgi/product_image.pl',
        query={'code': ingredient.code, 'id': image_id},
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
        'size': len(off_response.image_bytes),
    }
    try:
        Image.from_json(ingredient, off_response.response, image_data, generate_uuid=True)
    # Due to a race condition (e.g. when adding tasks over the search), we might
    # try to save an image to an ingredient that already has one. In that case,
    # just ignore the error
    except IntegrityError:
        logger.debug('Ingredient has already an image, skipping...')
        return
    ingredient.last_image_check = timezone.now()
    ingredient.save()
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
    language_codes: Optional[str] = None,
    style_fn=lambda x: x,
    show_progress_bar: bool = False,
):
    """Synchronize the ingredients from the remote server"""
    print_fn('*** Synchronizing ingredients...')

    language_ids: List[str] | None = None
    if language_codes is not None:
        language_ids = []
        for code in language_codes.split(','):
            # Leaving the try except in here even though we've already validated on the sync-ingredients command itself.
            # This is in case we ever want to re-use this function for anything else where user can input language codes.
            try:
                lang = load_language(code, default_to_english=False)
                language_ids.append(str(lang.id))
            except Language.DoesNotExist as e:
                print_fn(
                    f'Error: The language code you provided ("{code}") does not exist in this database. Please try again.'
                )
                return 0

    query: dict[str, str | int] = {'limit': API_MAX_ITEMS}
    if language_ids is not None:
        query['language__in'] = ','.join(language_ids)

    url = make_uri(
        INGREDIENTS_ENDPOINT,
        server_url=remote_url,
        query=query,
    )

    # Fetch once to retrieve the number of results
    response = requests.get(url, headers=wger_headers()).json()
    total_ingredients = response['count']
    total_pages = total_ingredients // API_MAX_ITEMS

    ingredient_nr = 1
    page_nr = 1
    pbar = tqdm(
        total=total_ingredients, unit='ingredients', desc='Syncing progress', unit_scale=True
    )
    for data in get_paginated(url, headers=wger_headers()):
        uuid = data['uuid']

        ingredient_data = extract_info_from_wger_api(data).dict()
        ingredient_data['uuid'] = uuid

        Ingredient.objects.update_or_create(uuid=uuid, defaults=ingredient_data)

        if show_progress_bar:
            pbar.update(1)
        else:
            # Note that get_paginated returns the individual result entries from the pages.
            # To get the current page, we need to calculate this ourselves.
            ingredient_nr += 1
            if ingredient_nr % API_MAX_ITEMS == 0:
                page_nr += 1
                print_fn(f'Processing ingredients, page {page_nr: >4} of {total_pages}')

    pbar.close()

    print_fn(style_fn('done!\n'))
    return None
