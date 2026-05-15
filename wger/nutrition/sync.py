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
import gzip
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import (
    List,
    Optional,
)

# Django
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.core.files.storage import default_storage
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
    INGREDIENT_BULK_EXPORT_PATH,
    INGREDIENTS_ENDPOINT,
    INGREDIENTS_SYNC_ENDPOINT,
)
from wger.nutrition.api.serializers import IngredientSerializer
from wger.nutrition.consts import SyncMode
from wger.nutrition.dataclasses import WeightUnitData
from wger.nutrition.extract_info.wger import (
    extract_info_from_wger_api,
    extract_weight_unit_info_from_wger_api,
)
from wger.nutrition.models import (
    Image,
    Ingredient,
    IngredientWeightUnit,
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


def _resolve_language_codes(language_codes: Optional[str]) -> List[str] | None:
    """Resolve comma-separated language codes to a list of language ID strings."""
    if language_codes is None:
        return None

    language_ids = []
    for code in language_codes.split(','):
        lang = load_language(code, default_to_english=False)
        language_ids.append(str(lang.id))
    return language_ids


def _sync_ingredient_from_api_data(data: dict) -> Ingredient:
    """
    Create or update a single ingredient (and its weight units) from API data.
    """
    uuid = data['uuid']
    ingredient_data = extract_info_from_wger_api(data).dict()
    ingredient_data['uuid'] = uuid

    ingredient, _ = Ingredient.objects.update_or_create(uuid=uuid, defaults=ingredient_data)
    weight_units_data = extract_weight_unit_info_from_wger_api(data)
    if weight_units_data is not None:
        sync_weight_units(ingredient, weight_units_data)

    return ingredient


def sync_weight_units(ingredient: Ingredient, weight_units_data: list[WeightUnitData]):
    """
    Synchronize weight units for an ingredient from remote data.
    """

    remote_uuids = set()
    for unit_data in weight_units_data:
        remote_uuids.add(unit_data.uuid)
        IngredientWeightUnit.objects.update_or_create(
            uuid=unit_data.uuid,
            defaults={
                'ingredient': ingredient,
                'name': unit_data.name,
                'gram': unit_data.gram,
            },
        )

    # Remove local units that no longer exist on the remote
    ingredient.ingredientweightunit_set.exclude(uuid__in=remote_uuids).delete()


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
        try:
            image = Image.from_json(ingredient, retrieved_image, image_data)
        except ValidationError as e:
            logger.warning(f'Skipping invalid ingredient image: {"; ".join(e.messages)}')
            return
        image.ingredient.last_image_check = timezone.now()
        image.ingredient.save()


def fetch_image_from_off(ingredient: Ingredient):
    """
    Tries to download an image from Open Food Facts for the given ingredient.

    See https://github.com/openfoodfacts/openfoodfacts-python
    """

    logger.info(f'Trying to fetch image from OFF for "{ingredient.name}" ({ingredient.uuid})')

    # We always update the last check time, no matter if we found an image or there were
    # errors in the response (keys missing, etc.) since in any case we don't want to retry
    # too often.
    ingredient.last_image_check = timezone.now()
    ingredient.save()

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
    image_data = product_data.get('images')
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
    except ValidationError as e:
        logger.warning(f'Skipping invalid ingredient image: {"; ".join(e.messages)}')
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
            try:
                Image.from_json(ingredient, retrieved_image, image_data)
            except ValidationError as e:
                print_fn(style_fn(f'    invalid image, skipping: {"; ".join(e.messages)}'))
                continue

        print_fn(style_fn('    successfully saved'))


def sync_ingredients(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    language_codes: Optional[str] = None,
    style_fn=lambda x: x,
    show_progress_bar: bool = False,
    last_update_gt: Optional[str] = None,
    id_gte: Optional[int] = None,
    id_lt: Optional[int] = None,
):
    """
    Synchronize ingredients from a remote wger instance

    Uses /api/v2/ingredient-sync which is backed by an indexed cursor instead
    of /api/v2/ingredientinfo which is OFFSET-based.

    For incremental syncs, pass an ISO-8601 timestamp via `last_update_gt` to
    only fetch ingredients that changed since the last sync.

    For parallel range-based syncs (used by the celery orchestrator), pass
    `id_gte` and/or `id_lt` to restrict the worker to one slice of the id
    space; combined with cursor pagination this is fast at any catalogue size.
    """
    print_fn('*** Synchronizing ingredients...')

    try:
        language_ids = _resolve_language_codes(language_codes)
    except Language.DoesNotExist:
        print_fn(
            'Error: A language code you provided does not exist in this database. Please try again.'
        )
        return 0

    filter_query: dict[str, str] = {}
    if language_ids is not None:
        filter_query['language__in'] = ','.join(language_ids)
    if last_update_gt:
        filter_query['last_update__gt'] = last_update_gt
    if id_gte is not None:
        filter_query['id__gte'] = str(id_gte)
    if id_lt is not None:
        filter_query['id__lt'] = str(id_lt)

    # Total count is only used for the progress bar's ETA / percentage. Skip
    # the probe when nobody is watching (e.g. inside the celery range-worker)
    # to avoid an unnecessary request against the throttled `ingredient_list`
    # scope.
    total = None
    if show_progress_bar:
        count_url = make_uri(
            INGREDIENTS_ENDPOINT,
            server_url=remote_url,
            query={**filter_query, 'limit': 1},
        )
        try:
            count_response = requests.get(count_url, headers=wger_headers(), timeout=30).json()
            total = count_response.get('count')
        except (requests.RequestException, ValueError) as e:
            logger.info(f'Could not fetch total ingredient count: {e}')

    url = make_uri(
        INGREDIENTS_SYNC_ENDPOINT,
        server_url=remote_url,
        query={**filter_query, 'page_size': API_MAX_ITEMS},
    )

    pbar = tqdm(
        total=total,
        unit='ingredients',
        desc='Syncing progress',
        unit_scale=True,
        smoothing=0.1,
        mininterval=1.0,
        disable=not show_progress_bar,
    )

    count = 0
    errors = 0
    for data in get_paginated(url, headers=wger_headers()):
        try:
            _sync_ingredient_from_api_data(data)
        except (KeyError, ValueError, TypeError) as e:
            # A single malformed or invalid record must not abort the whole run
            errors += 1
            logger.warning(f'Skipping malformed ingredient during sync: {e}')
            continue
        count += 1
        pbar.update(1)
        if not show_progress_bar and count % API_MAX_ITEMS == 0:
            print_fn(f'Processed {count} ingredients...')

    pbar.close()

    print_fn(style_fn(f'done! Processed {count} ingredients ({errors} errors).\n'))
    return count


BULK_SIZE = 500


def export_ingredient_dump(
    print_fn,
    style_fn=lambda x: x,
    show_progress_bar: bool = False,
):
    """
    Export all ingredients as a gzipped JSONL file via Django's default storage.

    Each line is the same JSON format as the ingredient API endpoint,
    so clients can parse it with extract_info_from_wger_api().

    Uses default_storage so the dump works with any configured backend
    (local filesystem, S3, GCS, etc.).
    """

    queryset = Ingredient.objects.select_related(
        'language',
        'license',
    ).prefetch_related('ingredientweightunit_set')
    total = queryset.count()
    queryset = queryset.iterator(chunk_size=2000)

    print_fn('*** Exporting ingredients to JSONL dump...')

    pbar = tqdm(
        total=total,
        unit='ingredients',
        desc='Exporting',
        disable=not show_progress_bar,
        smoothing=0.1,
        mininterval=1.0,
    )

    # Write to a local temp file first, then upload via storage backend
    count = 0
    with tempfile.NamedTemporaryFile(suffix='.jsonl.gz', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        with gzip.open(tmp_path, 'wt', encoding='utf-8') as f:
            for ingredient in queryset:
                data = IngredientSerializer(ingredient).data
                f.write(json.dumps(data) + '\n')
                count += 1
                pbar.update(1)

        pbar.close()

        # Upload to the configured storage backend
        with open(tmp_path, 'rb') as f:
            # delete old file first if it exists, then save the new one
            if default_storage.exists(INGREDIENT_BULK_EXPORT_PATH):
                default_storage.delete(INGREDIENT_BULK_EXPORT_PATH)
            saved_name = default_storage.save(INGREDIENT_BULK_EXPORT_PATH, File(f))
    finally:
        Path(tmp_path).unlink()

    print_fn(style_fn(f'done! Exported {count} ingredients to {saved_name}\n'))
    return saved_name


def _open_jsonl(file_path: Path):
    """Open a JSONL file, transparently handling both gzip and plain text."""
    with open(file_path, 'rb') as f:
        magic = f.read(2)
    if magic == b'\x1f\x8b':
        return gzip.open(file_path, 'rt', encoding='utf-8')
    return open(file_path, 'r', encoding='utf-8')


def sync_ingredients_from_dump(
    print_fn,
    file_path: Path,
    mode: SyncMode = SyncMode.UPDATE,
    style_fn=lambda x: x,
    show_progress_bar: bool = False,
):
    """
    Import ingredients from a JSONL dump file (gzipped or plain).

    Each line must be in the same JSON format as the ingredient API endpoint.
    Reuses extract_info_from_wger_api() for data transformation.
    """
    print_fn(f'*** Importing ingredients from {file_path} (mode: {mode.name})...')

    # Count lines for the progress bar
    total = 0
    if show_progress_bar:
        with _open_jsonl(file_path) as f:
            total = sum(1 for _ in f)

    pbar = tqdm(
        total=total,
        unit='ingredients',
        desc='Importing',
        disable=not show_progress_bar,
        smoothing=0.1,
        mininterval=1.0,
    )

    bulk_bucket: List[tuple[Ingredient, list[WeightUnitData] | None]] = []
    count = 0
    errors = 0

    with _open_jsonl(file_path) as f:
        for line in f:
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                errors += 1
                continue

            uuid = data.get('uuid')
            if not uuid:
                errors += 1
                continue

            try:
                ingredient_data = extract_info_from_wger_api(data).dict()
            except (KeyError, ValueError, TypeError):
                # A single malformed or invalid record must not abort the import
                errors += 1
                continue
            ingredient_data['uuid'] = uuid
            weight_units_data = extract_weight_unit_info_from_wger_api(data)

            if mode == SyncMode.INSERT:
                bulk_bucket.append((Ingredient(**ingredient_data), weight_units_data))
                if len(bulk_bucket) >= BULK_SIZE:
                    try:
                        Ingredient.objects.bulk_create([item[0] for item in bulk_bucket])
                        # Re-fetch to ensure PKs are populated (not all DBs
                        # return PKs from bulk_create)
                        uuids = [item[0].uuid for item in bulk_bucket]
                        saved = {str(i.uuid): i for i in Ingredient.objects.filter(uuid__in=uuids)}
                        for ingredient, units_data in bulk_bucket:
                            refetched = saved.get(str(ingredient.uuid))
                            if units_data is not None and refetched is not None:
                                sync_weight_units(refetched, units_data)
                        count += len(bulk_bucket)
                    except Exception:
                        # Fall back to individual saves
                        for ingredient, units_data in bulk_bucket:
                            try:
                                ingredient.save()
                                if units_data is not None:
                                    sync_weight_units(ingredient, units_data)
                                count += 1
                            except Exception:
                                errors += 1
                    bulk_bucket = []
            else:
                try:
                    ingredient, _ = Ingredient.objects.update_or_create(
                        uuid=uuid, defaults=ingredient_data
                    )
                    if weight_units_data is not None:
                        sync_weight_units(ingredient, weight_units_data)
                    count += 1
                except Exception:
                    errors += 1

            pbar.update(1)

    # Flush remaining items in INSERT mode
    if mode == SyncMode.INSERT and bulk_bucket:
        try:
            Ingredient.objects.bulk_create([item[0] for item in bulk_bucket])
            uuids = [item[0].uuid for item in bulk_bucket]
            saved = {i.uuid: i for i in Ingredient.objects.filter(uuid__in=uuids)}
            for ingredient, units_data in bulk_bucket:
                if units_data is not None and ingredient.uuid in saved:
                    sync_weight_units(saved[ingredient.uuid], units_data)
            count += len(bulk_bucket)
        except Exception:
            for ingredient, units_data in bulk_bucket:
                try:
                    ingredient.save()
                    if units_data is not None:
                        sync_weight_units(ingredient, units_data)
                    count += 1
                except Exception:
                    errors += 1

    pbar.close()

    print_fn(style_fn(f'done! Processed {count} ingredients ({errors} errors)\n'))
    return count


def download_ingredient_dump(
    print_fn,
    remote_url: str = settings.WGER_SETTINGS['WGER_INSTANCE'],
    folder: str = '',
    style_fn=lambda x: x,
) -> Path:
    """
    Download the ingredient JSONL dump from a remote wger instance.

    Returns the path to the downloaded file.
    """

    dump_url = settings.WGER_SETTINGS.get(
        'SYNC_INGREDIENTS_DUMP_URL',
        f'{remote_url}{settings.MEDIA_URL}{INGREDIENT_BULK_EXPORT_PATH}',
    )
    print_fn(f'*** Downloading ingredient dump from {dump_url}...')

    if folder:
        file_path = Path(folder) / 'ingredients.jsonl.gz'
        if file_path.exists():
            print_fn(f'File already downloaded at {file_path}')
            return file_path
    else:
        file_path = Path(tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl.gz').name)

    response = requests.get(dump_url, stream=True, headers=wger_headers(), timeout=(10, 60))
    if response.status_code == 404:
        raise FileNotFoundError(
            f'Bulk ingredient dump not found at {dump_url}. '
            f'The remote server may not have generated a dump yet. '
            f'Please ask the server admin to run "python manage.py export-ingredients" first.'
        )
    if response.status_code != 200:
        raise Exception(f'Could not download dump from {dump_url} (status {response.status_code})')

    # Prevent requests from transparently decompressing the gzip file
    response.raw.decode_content = False
    total_size = int(response.headers.get('content-length', 0))

    with open(file_path, 'wb') as fid:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading') as pbar:
            for chunk in response.raw.stream(50 * 1024):
                fid.write(chunk)
                pbar.update(len(chunk))

    print_fn(style_fn(f'Download complete: {file_path}\n'))
    return file_path
