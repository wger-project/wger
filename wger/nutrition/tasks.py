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
from django.core.cache import cache
from django.core.management import call_command

# Third Party
import requests
from celery import group
from celery.schedules import crontab

# wger
from wger.celery_configuration import app
from wger.nutrition.api.endpoints import INGREDIENTS_ENDPOINT
from wger.nutrition.sync import (
    download_ingredient_images,
    fetch_ingredient_image,
    sync_ingredients,
    sync_ingredients_page,
)
from wger.utils.cache import CacheKeyMapper
from wger.utils.constants import API_MAX_ITEMS
from wger.utils.requests import wger_headers
from wger.utils.url import make_uri


logger = logging.getLogger(__name__)


PAGE_RANGE_SIZE = 25
"""The number of pages (with API_MAX_ITEMS items each) the individual task processes"""


CACHE_TIMEOUT_SECONDS = 10 * 3600
"""Timeout for the cache keys marking completed pages/ranges"""


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
def sync_ingredient_page_range_task(
    total_pages: int,
    start_page: int,
    end_page: int,
    remote_url: str | None = None,
    language_codes: str | None = None,
):
    """
    Sequentially processes pages in [start_page, end_page), skips pages already
    completed by writing to the cache.
    """
    remote = remote_url or settings.WGER_SETTINGS['WGER_INSTANCE']
    processed = 0
    for page in range(start_page, end_page):
        # Atomic: only first caller succeeds; subsequent ones skip
        key = CacheKeyMapper.ingredient_celery_sync(page)
        if not cache.add(key, 'done', timeout=CACHE_TIMEOUT_SECONDS):
            logger.info(f'Page {page} already done, skipping.')
            continue

        page_processed = sync_ingredients_page(
            page=page,
            limit=API_MAX_ITEMS,
            remote_url=remote,
            language_codes=language_codes,
        )
        processed += page_processed
    logger.info(f'Processed pages {start_page} - {end_page - 1} of {total_pages}')
    return processed


@app.task
def sync_all_ingredients_chunked_task(
    language_codes: str | None = None,
    remote_url: str | None = None,
):
    """
    Orchestrator: builds a group of page-range tasks that process a range of pages each.
    Runs in parallel depending on the concurrency settings of the Celery worker.
    """

    # Calculate number of pages
    remote = remote_url or settings.WGER_SETTINGS['WGER_INSTANCE']
    url = make_uri(INGREDIENTS_ENDPOINT, server_url=remote, query={'limit': 1})
    data = requests.get(url, headers=wger_headers(), timeout=30).json()
    total = data['count']
    total_pages = total // API_MAX_ITEMS
    logger.info(
        f'Start sync: {total} ingredients over {total_pages} pages (chunk={PAGE_RANGE_SIZE}).'
    )

    # Create tasks for each page range and start them
    tasks = []
    for start in range(0, total_pages, PAGE_RANGE_SIZE):
        end = min(start + PAGE_RANGE_SIZE, total_pages)

        tasks.append(
            sync_ingredient_page_range_task.s(total_pages, start, end, remote, language_codes)
        )
    group(*tasks).apply_async()

    return None


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
            ),
            sync_all_ingredients_chunked_task.s(),
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
