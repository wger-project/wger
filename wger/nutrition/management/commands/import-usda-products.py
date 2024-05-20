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
from wger.nutrition.management.products import (
    ImportProductCommand,
    Mode,
)
from wger.nutrition.usda import extract_info_from_usda
from wger.utils.constants import ENGLISH_SHORT_NAME
from wger.utils.requests import wger_headers

logger = logging.getLogger(__name__)

# Check https://fdc.nal.usda.gov/download-datasets.html for current file names
# current_file = 'FoodData_Central_foundation_food_json_2024-04-18.zip'
current_file = 'FoodData_Central_branded_food_json_2024-04-18.zip'
download_folder = '/Users/roland/Entwicklung/wger/server/extras/usda'


class Command(ImportProductCommand):
    """
    Import an Open Food facts Dump
    """

    def handle(self, **options):
        if options['mode'] == 'insert':
            self.mode = Mode.INSERT

        usda_url = f'https://fdc.nal.usda.gov/fdc-datasets/{current_file}'

        self.stdout.write('Importing entries from USDA')
        self.stdout.write(f' - {self.mode}')
        self.stdout.write(f' - dataset: {usda_url}')
        self.stdout.write(f' - download folder: {download_folder}')
        self.stdout.write('')

        english = Language.objects.get(short_name=ENGLISH_SHORT_NAME)

        # Download the dataset
        zip_file = os.path.join(download_folder, current_file)
        if os.path.exists(zip_file):
            self.stdout.write(f'File already downloaded {zip_file}, not downloading it again')
        else:
            self.stdout.write(f'Downloading {zip_file}... (this may take a while)')
            req = requests.get(usda_url, stream=True, headers=wger_headers())
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
                else:
                    # pass
                    self.handle_data(ingredient_data)

        self.stdout.write(self.style.SUCCESS('Finished!'))
        self.stdout.write(self.style.SUCCESS(str(self.counter)))
