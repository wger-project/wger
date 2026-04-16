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
import json
import logging
import os
from gzip import GzipFile
from json import JSONDecodeError

# Django
from django.db.models import Count

# Third Party
from tqdm import tqdm

# wger
from wger.nutrition.consts import OFF_FULL_DUMP_URL
from wger.nutrition.management.products import ImportProductCommand
from wger.nutrition.models import (
    Ingredient,
    Source,
)


logger = logging.getLogger(__name__)


class Command(ImportProductCommand):
    """
    Scan the full Open Food Facts JSONL dump and identify local OFF ingredients
    whose code no longer exists upstream (i.e. deleted at OFF).

    This command is intended to be an early warning system for deleted products,
    so that we can decide how to handle them. At the time of writing (April 2026)
    only a bit more than 1% of ingredients were deleted in the OFF database, and
    just over 100 of those where used in a meal item or were logged, so no further
    action is required.

    Example usage:
    * Download the dump to a temporary folder, scan it, print a summary:
        python manage.py find-deleted-off-products

    * Reuse an already-downloaded dump:
        python manage.py find-deleted-off-products --folder /tmp/off/
    """

    help = 'Identify local OFF ingredients that were deleted upstream'

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            action='store',
            default='',
            dest='folder',
            type=str,
            help=(
                'Folder that contains (or will receive) the downloaded OFF dump. '
                'If empty, a temporary folder is used and cleaned up afterwards.'
            ),
        )

    def _scan_dump_for_codes(self, file_path: str) -> tuple[set[str], int]:
        """
        Collect every product code from the database dump

        Returns (codes, parse_errors)
        """
        self.stdout.write('Reading dump and collecting product codes...')
        off_codes: set[str] = set()
        parse_errors = 0
        with GzipFile(file_path, 'rb') as gzid:
            for line in tqdm(gzid, unit=' lines', unit_scale=True, desc='Scanning dump'):
                try:
                    product = json.loads(line)
                except JSONDecodeError:
                    parse_errors += 1
                    continue
                code = product.get('code')
                if code is not None:
                    off_codes.add(str(code))

        self.stdout.write(f' - {len(off_codes)} distinct codes in the dump')
        if parse_errors:
            self.stdout.write(f' - {parse_errors} lines could not be parsed')
        return off_codes, parse_errors

    def handle(self, **options):
        self.stdout.write('Scanning Open Food Facts DB dump for deleted products')

        # Fetch local OFF entries
        off_qs = Ingredient.objects.filter(
            source_name=Source.OPEN_FOOD_FACTS.value,
            remote_id__isnull=False,
        ).exclude(remote_id='')
        local_count = off_qs.count()
        self.stdout.write(f' - {local_count} local OFF ingredient')

        # Download or locate the dump
        download_folder, tmp_folder = self.get_download_folder(options['folder'])
        file_path = os.path.join(download_folder, os.path.basename(OFF_FULL_DUMP_URL))
        self.download_file(OFF_FULL_DUMP_URL, file_path)

        # Process
        off_count, parse_errors = self._scan_dump_for_codes(file_path)
        if tmp_folder:
            self.stdout.write(f'Removing temporary folder {download_folder}')
            tmp_folder.cleanup()

        self.stdout.write('Loading local OFF remote_ids...')
        local_remote_ids = set(
            off_qs.values_list('remote_id', flat=True).iterator(chunk_size=50_000)
        )
        self.stdout.write(f' - {len(local_remote_ids)} local remote_ids loaded')
        missing_ids = local_remote_ids - off_count
        self.stdout.write(f' - {len(missing_ids)} not found in the dump')

        # Fetch details only for the (hopefully small) set of missing ones
        missing_qs = (
            off_qs.filter(remote_id__in=missing_ids)
            .annotate(
                meal_item_count=Count('mealitem', distinct=True),
                log_item_count=Count('logitem', distinct=True),
            )
            .order_by('pk')
        )

        in_use = 0
        orphaned = 0
        for ingredient in missing_qs.iterator():
            if ingredient.meal_item_count or ingredient.log_item_count:
                in_use += 1
            else:
                orphaned += 1

        self.stdout.write('')
        self.stdout.write('Summary')
        self.stdout.write(f'* ingredients in local db: {local_count}')
        self.stdout.write(f'* ingredients in OFF db: {len(off_count)}')
        self.stdout.write(f'* missing (total): {len(missing_ids)}')
        self.stdout.write(f'* missing (orphaned): {orphaned}')
        self.stdout.write(f'* missing (in use): {in_use}')
        self.stdout.write(f'* parse errors: {parse_errors}')

        self.stdout.write(self.style.SUCCESS('Finished!'))
