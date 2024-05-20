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
import tempfile
from json import JSONDecodeError
from zipfile import ZipFile

# Third Party
import requests

# wger
from wger.core.models import Language
from wger.nutrition.dataclasses import IngredientData
from wger.nutrition.management.products import (
    ImportProductCommand,
    Mode,
)
from wger.nutrition.models import Ingredient
from wger.nutrition.usda import extract_info_from_usda
from wger.utils.constants import ENGLISH_SHORT_NAME
from wger.utils.requests import wger_headers


logger = logging.getLogger(__name__)


class Command(ImportProductCommand):
    """
    Import an USDA dataset
    """

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--use-folder',
            action='store',
            default='',
            dest='tmp_folder',
            type=str,
            help='Controls whether to use a temporary folder created by python (the default) or '
            'the path provided for storing the downloaded dataset. If there are already '
            'downloaded or extracted files here, they will be used instead of fetching them '
            'again.',
        )

        parser.add_argument(
            '--dataset-name',
            action='store',
            default='FoodData_Central_branded_food_json_2024-04-18.zip',
            dest='dataset_name',
            type=str,
            help='What dataset to download, this value will be appended to '
            '"https://fdc.nal.usda.gov/fdc-datasets/". Consult '
            'https://fdc.nal.usda.gov/download-datasets.html for current file names',
        )

    def handle(self, **options):
        if options['mode'] == 'insert':
            self.mode = Mode.INSERT

        usda_url = f'https://fdc.nal.usda.gov/fdc-datasets/{options["dataset_name"]}'

        if options['tmp_folder']:
            download_folder = options['tmp_folder']

            # Check whether the folder exists
            if not os.path.exists(download_folder):
                self.stdout.write(self.style.ERROR(f'Folder {download_folder} does not exist!'))
                return
        else:
            tmp_folder = tempfile.TemporaryDirectory()
            download_folder = tmp_folder.name

        self.stdout.write('Importing entries from USDA')
        self.stdout.write(f' - {self.mode}')
        self.stdout.write(f' - dataset: {usda_url}')
        self.stdout.write(f' - download folder: {download_folder}')
        self.stdout.write('')

        english = Language.objects.get(short_name=ENGLISH_SHORT_NAME)

        # Download the dataset
        zip_file = os.path.join(download_folder, options['dataset_name'])
        if os.path.exists(zip_file):
            self.stdout.write(f'File already downloaded {zip_file}, not downloading it again')
        else:
            self.stdout.write(f'Downloading {usda_url}... (this may take a while)')
            req = requests.get(usda_url, stream=True, headers=wger_headers())

            if req.status_code == 404:
                self.stdout.write(self.style.ERROR(f'Could not open {usda_url}!'))
                return

            with open(zip_file, 'wb') as fid:
                for chunk in req.iter_content(chunk_size=50 * 1024):
                    fid.write(chunk)

            self.stdout.write('download successful')

        # Extract the first file from the ZIP archive
        with ZipFile(zip_file, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            if not file_list:
                raise Exception('No files found in the ZIP archive')

            first_file = file_list[0]

            # If the file was already extracted to the download folder, skip
            extracted_file_path = os.path.join(download_folder, first_file)
            if os.path.exists(extracted_file_path):
                self.stdout.write(f'File {first_file} already extracted, skipping...')
            else:
                self.stdout.write(f'Extracting {first_file}...')
                extracted_file_path = zip_ref.extract(first_file, path=download_folder)

        # Since the file is almost JSONL, just process each line individually
        with open(extracted_file_path, 'r') as extracted_file:
            for line in extracted_file.readlines():
                # Try to skip the first and last lines in the file
                if 'FoundationFoods' in line or 'BrandedFoods' in line:
                    continue

                if line.strip() == '}':
                    continue

                try:
                    json_data = json.loads(line.strip().strip(','))
                except JSONDecodeError as e:
                    self.stdout.write(f'--> Error while decoding JSON: {e}')
                    continue

                try:
                    ingredient_data = extract_info_from_usda(json_data, english.pk)
                except KeyError as e:
                    self.stdout.write(f'--> KeyError while extracting ingredient info: {e}')
                    self.counter['skipped'] += 1
                except ValueError as e:
                    self.stdout.write(f'--> ValueError while extracting ingredient info: {e}')
                    self.counter['skipped'] += 1
                else:
                    # pass
                    self.match_existing_entry(ingredient_data)
                    # self.handle_data(ingredient_data)

        if not options['tmp_folder']:
            self.stdout.write(f'Removing temporary folder {download_folder}')
            tmp_folder.cleanup()

        self.stdout.write(self.style.SUCCESS('Finished!'))
        self.stdout.write(self.style.SUCCESS(str(self.counter)))

    def match_existing_entry(self, ingredient_data: IngredientData):
        """
        One-off method.

        There are currently some entries in the database that were imported from an old USDA
        import but neither the original script nor the dump are available anymore, so we can't
        really know which ones they are.

        This method tries to match the ingredient_data.name with the name of an existing entry
        and set the remote_id so that these can be updated regularly in the future.
        """
        try:
            obj, created = Ingredient.objects.update_or_create(
                name__iexact=ingredient_data.name,
                code=None,
                defaults=ingredient_data.dict(),
            )

            if created:
                self.counter['new'] += 1
                # self.stdout.write('-> added to the database')
            else:
                self.counter['edited'] += 1
                self.stdout.write(f'-> found and updated {obj.name}')

        except Exception as e:
            # self.stdout.write('--> Error while performing update_or_create')
            # self.stdout.write(repr(e))
            # self.stdout.write(repr(ingredient_data))
            self.counter['error'] += 1
