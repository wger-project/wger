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
from random import randint

# Django
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError

# Third Party
import requests
from celery import group
from celery.schedules import crontab

# wger
from wger.celery_configuration import app
from wger.core.api.min_server_version import check_min_server_version
from wger.nutrition.api.endpoints import INGREDIENTS_ENDPOINT
from wger.nutrition.sync import (
    download_ingredient_dump,
    download_ingredient_images,
    export_ingredient_dump,
    fetch_ingredient_image,
    sync_ingredients,
    sync_ingredients_from_dump,
)
from wger.utils.requests import wger_headers
from wger.utils.url import make_uri


logger = logging.getLogger(__name__)


ID_RANGE_SIZE = 25_000
"""Approx. ingredients processed per parallel celery worker.

We split the id space [0, max_id] into chunks of this size and dispatch one
task per chunk via celery group. Within each chunk, sync_ingredients() walks
via cursor pagination — fast at any catalogue size.
"""


@app.task
def fetch_ingredient_image_task(pk: int):
    """
    Fetches the ingredient image from an upstream wger server (or Open Food Facts)
    if it is not available locally.
    """
    fetch_ingredient_image(pk)


@app.task
def fetch_all_ingredient_images_task():
    """
    Fetches all ingredient image from an upstream wger server (or Open Food Facts)
    if they are not available locally
    """
    download_ingredient_images(logger.info)


@app.task(
    autoretry_for=(requests.exceptions.RequestException,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={'max_retries': 5},
)
def sync_ingredient_id_range_task(
    id_gte: int,
    id_lt: int,
    remote_url: str | None = None,
    language_codes: str | None = None,
):
    """
    Sync the ingredients in `[id_gte, id_lt)` via the cursor endpoint.

    One celery worker handles one slice of the id space. Cursor pagination
    inside the slice means each page is an indexed lookup (O(log n)), so the
    overall load on the remote scales linearly with the catalogue size — no
    deep-OFFSET penalty.

    Idempotent: `update_or_create` in `_sync_ingredient_from_api_data` makes
    re-running the same range safe. A failed worker simply retries (autoretry
    above) or is replayed by celery without leaving the local DB inconsistent.
    """
    remote = remote_url or settings.WGER_SETTINGS['WGER_INSTANCE']
    logger.info(f'Sync id range [{id_gte}, {id_lt})')
    sync_ingredients(
        logger.info,
        remote_url=remote,
        language_codes=language_codes,
        id_gte=id_gte,
        id_lt=id_lt,
    )


@app.task
def sync_all_ingredients_chunked_task(
    language_codes: str | None = None,
    remote_url: str | None = None,
):
    """
    Orchestrator: splits the id space into ranges of `ID_RANGE_SIZE` rows each
    and dispatches a parallel task per range. Each worker uses cursor
    pagination internally (see sync_ingredient_id_range_task).

    Replaces the previous OFFSET-based chunking, which scaled quadratically
    with catalogue size and triggered minute-long queries on the remote at
    high page numbers.
    """

    remote = remote_url or settings.WGER_SETTINGS['WGER_INSTANCE']

    try:
        check_min_server_version(remote)
    except CommandError as e:
        logger.error(f'Ingredient sync aborted, server incompatible: {e}')
        return None

    # Find the highest existing id on the remote so we know how far to chunk.
    url = make_uri(
        INGREDIENTS_ENDPOINT,
        server_url=remote,
        query={'ordering': '-id', 'limit': 1},
    )
    data = requests.get(url, headers=wger_headers(), timeout=30).json()
    if data.get('count', 0) == 0:
        logger.info('Remote has no ingredients, nothing to sync.')
        return None

    max_id = data['results'][0]['id']
    total = data['count']
    logger.info(
        f'Start sync: {total} ingredients up to id={max_id}, chunk size={ID_RANGE_SIZE} rows.'
    )

    # Dispatch one task per id range. The last range covers max_id; ranges
    # past max_id never execute because no rows match.
    tasks = []
    for start in range(0, max_id + 1, ID_RANGE_SIZE):
        end = start + ID_RANGE_SIZE
        tasks.append(sync_ingredient_id_range_task.s(start, end, remote, language_codes))
    group(*tasks).apply_async()

    return None


@app.task(
    autoretry_for=(requests.exceptions.RequestException,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={'max_retries': 3},
)
def sync_ingredients_bulk_or_api_task():
    """
    Sync ingredients from a remote wger instance.

    Tries to download a bulk JSONL dump first. If the dump is not available
    (e.g. the remote server hasn't generated one), falls back to the paginated
    API sync.
    """
    try:
        check_min_server_version(settings.WGER_SETTINGS['WGER_INSTANCE'])
    except CommandError as e:
        logger.error(f'Ingredient sync aborted, server incompatible: {e}')
        return

    try:
        file_path = download_ingredient_dump(logger.info)
        try:
            sync_ingredients_from_dump(logger.info, file_path)
        finally:
            file_path.unlink(missing_ok=True)
    except FileNotFoundError:
        logger.info('Bulk dump not available, falling back to API sync.')
        sync_all_ingredients_chunked_task.delay()


@app.task
def export_ingredients_dump_task():
    """
    Export all ingredients as a gzipped JSONL file for bulk synchronization.
    """
    export_ingredient_dump(logger.info)


@app.task
def sync_off_daily_delta():
    """
    Fetches OFF's daily delta product updates
    """
    call_command('import-off-products', '--delta-updates')


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):

    # Sync ingredients via celery once a month (prefers bulk dump, falls back to API)
    if settings.WGER_SETTINGS['SYNC_INGREDIENTS_CELERY']:
        sender.add_periodic_task(
            crontab(
                hour=str(randint(0, 23)),
                minute=str(randint(0, 59)),
                day_of_month=str(randint(1, 28)),
            ),
            sync_ingredients_bulk_or_api_task.s(),
            name='Sync ingredients',
        )

    # Generate the ingredient export on the 1st and 15th of every month
    if settings.WGER_SETTINGS['EXPORT_INGREDIENTS_BULK_CELERY']:
        sender.add_periodic_task(
            crontab(
                hour=str(randint(0, 23)),
                minute=str(randint(0, 59)),
                day_of_month='1,15',
            ),
            export_ingredients_dump_task.s(),
            name='Export ingredients bulk dump',
        )

    # Sync the OFF daily delta updates once a day
    if settings.WGER_SETTINGS['SYNC_OFF_DAILY_DELTA_CELERY']:
        sender.add_periodic_task(
            crontab(
                hour=str(randint(0, 23)),
                minute=str(randint(0, 59)),
            ),
            sync_off_daily_delta.s(),
            name='Sync OFF daily delta updates',
        )
