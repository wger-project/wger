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
import enum
import json
import logging
import os
import tempfile
from collections import Counter
from gzip import GzipFile
from json import JSONDecodeError
from typing import Optional

# Django
from django.core.management.base import BaseCommand

# Third Party
import requests
from tqdm import tqdm

# wger
from wger.nutrition.dataclasses import IngredientData
from wger.nutrition.models import Ingredient
from wger.utils.requests import wger_headers


logger = logging.getLogger(__name__)


# Mode for this script. When using 'insert', the script will bulk-insert the new
# ingredients, which is very efficient. Importing the whole database will require
# barely a minute. When using 'update', existing ingredients will be updated, which
# requires two queries per product and is needed when there are already existing
# entries in the local ingredient table.
class Mode(enum.Enum):
    INSERT = enum.auto()
    UPDATE = enum.auto()


class ImportProductCommand(BaseCommand):
    """
    Import an Open Food facts Dump
    """

    mode = Mode.UPDATE
    bulk_update_bucket: list[Ingredient] = []
    bulk_size = 500
    counter: Counter

    help = "Don't run this command directly. Use either import-off-products or import-usda-products"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.counter = Counter()

    def add_arguments(self, parser):
        parser.add_argument(
            '--set-mode',
            action='store',
            default='update',
            dest='mode',
            type=str,
            help=(
                'Script mode, "insert" or "update". Insert will insert the ingredients as new '
                'entries in the database, while update will try to update them if they are '
                'already present. Default: update'
            ),
        )

        parser.add_argument(
            '--folder',
            action='store',
            default='',
            dest='folder',
            type=str,
            help=(
                'Controls whether to use a temporary folder created by python (the default) or '
                'the path provided for storing the downloaded dataset. If there are already '
                'downloaded or extracted files here, they will be used instead of fetching them '
                'again.'
            ),
        )

    def handle(self, **options):
        raise NotImplementedError('Do not run this command on its own!')

    def process_ingredient(self, ingredient_data: IngredientData):
        #
        # Add entries as new products
        if self.mode == Mode.INSERT:
            self.bulk_update_bucket.append(Ingredient(**ingredient_data.dict()))
            if len(self.bulk_update_bucket) > self.bulk_size:
                try:
                    Ingredient.objects.bulk_create(self.bulk_update_bucket)
                    self.stdout.write('***** Bulk adding products *****')
                except Exception as e:
                    self.stdout.write(
                        '--> Error while saving the product bucket. Saving individually'
                    )
                    self.stdout.write(e)

                    # Try saving the ingredients individually as most will be correct
                    for ingredient in self.bulk_update_bucket:
                        try:
                            ingredient.save()

                        # ¯\_(ツ)_/¯
                        except Exception as e:
                            self.stdout.write('--> Error while saving the product individually')
                            self.stdout.write(e)

                self.counter['new'] += self.bulk_size
                self.bulk_update_bucket = []

        # Update existing entries
        else:
            try:
                # Update an existing product (look-up key is the code) or create a new
                # one. While this might not be the most efficient query (there will always
                # be a SELECT first), it's ok because this script is run very rarely.
                obj, created = Ingredient.objects.update_or_create(
                    remote_id=ingredient_data.remote_id,
                    defaults=ingredient_data.dict(),
                )

                if created:
                    self.counter['new'] += 1
                    # self.stdout.write('-> added to the database')
                else:
                    self.counter['edited'] += 1
                    # self.stdout.write('-> updated')

            except Exception as e:
                self.stdout.write(f'--> Error while performing update_or_create: {e}')
                self.stdout.write(repr(ingredient_data))
                self.counter['error'] += 1

    def get_download_folder(self, folder: str) -> tuple[str, Optional[tempfile.TemporaryDirectory]]:
        if folder:
            tmp_folder = None
            download_folder = folder

            # Check whether the folder exists
            if not os.path.exists(download_folder):
                self.stdout.write(self.style.ERROR(f'Folder {download_folder} does not exist!'))
                raise Exception('Folder does not exist')
        else:
            tmp_folder = tempfile.TemporaryDirectory()
            download_folder = tmp_folder.name

        self.stdout.write(f'Using folder {download_folder} for storing downloaded files')
        return download_folder, tmp_folder

    def iterate_gz_file_contents(self, path: str, languages: list[str]):
        with GzipFile(path, 'rb') as gzid:
            for line in gzid:
                try:
                    product = json.loads(line)
                    if not product.get('lang') in languages:
                        continue
                    yield product
                except JSONDecodeError:
                    self.stdout.write(f' Error parsing and/or filtering  json record, skipping')
                    continue

    def download_file(self, url: str, destination: str) -> None:
        if os.path.exists(destination):
            self.stdout.write(f'File already downloaded at {destination}')
            return

        self.stdout.write(f'Downloading {url}... (this may take a while)')
        response = requests.get(url, stream=True, headers=wger_headers())
        total_size = int(response.headers.get('content-length', 0))

        if response.status_code == 404:
            raise Exception(f'Could not open {url}!')

        with open(destination, 'wb') as fid:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading') as pbar:
                for chunk in response.iter_content(chunk_size=50 * 1024):
                    fid.write(chunk)
                    pbar.update(len(chunk))
