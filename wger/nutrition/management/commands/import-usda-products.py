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
from json import JSONDecodeError
from zipfile import ZipFile

# wger
from wger.core.models import Language
from wger.nutrition.management.products import (
    ImportProductCommand,
    Mode,
)
from wger.nutrition.usda import extract_info_from_usda
from wger.utils.constants import ENGLISH_SHORT_NAME


logger = logging.getLogger(__name__)


class Command(ImportProductCommand):
    """
    Import an USDA dataset
    """

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--dataset',
            action='store',
            default='FoodData_Central_branded_food_json_2024-04-18.zip',
            dest='dataset',
            type=str,
            help='What dataset to download, this value will be appended to '
            '"https://fdc.nal.usda.gov/fdc-datasets/". Consult '
            'https://fdc.nal.usda.gov/download-datasets.html for current file names',
        )

    def handle(self, **options):
        if options['mode'] == 'insert':
            self.mode = Mode.INSERT

        dataset_url = f'https://fdc.nal.usda.gov/fdc-datasets/{options["dataset"]}'
        download_folder, tmp_folder = self.get_download_folder(options['folder'])

        self.stdout.write('Importing entries from USDA')
        self.stdout.write(f' - {self.mode}')
        self.stdout.write(f' - dataset: {dataset_url}')
        self.stdout.write(f' - download folder: {download_folder}')
        self.stdout.write('')

        english = Language.objects.get(short_name=ENGLISH_SHORT_NAME)

        # Download the dataset
        zip_file_path = os.path.join(download_folder, options['dataset'])
        self.download_file(dataset_url, zip_file_path)

        # Extract the first file from the ZIP archive
        with ZipFile(zip_file_path, 'r') as zip_ref:
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
        self.stdout.write('Start processing...')
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
                    self.process_ingredient(ingredient_data)

        if tmp_folder:
            self.stdout.write(f'Removing temporary folder {download_folder}')
            tmp_folder.cleanup()

        self.stdout.write(self.style.SUCCESS('Finished!'))
        self.stdout.write(self.style.SUCCESS(str(self.counter)))
