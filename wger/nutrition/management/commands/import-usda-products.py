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
from json import JSONDecodeError
from zipfile import ZipFile

import requests

# Django
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


# Mode for this script. When using 'insert', the script will bulk-insert the new
# ingredients, which is very efficient. Importing the whole database will require
# barely a minute. When using 'update', existing ingredients will be updated, which
# requires two queries per product and is needed when there are already existing
# entries in the local ingredient table.
class Mode(enum.Enum):
    INSERT = enum.auto()
    UPDATE = enum.auto()


class Command(BaseCommand):
    """
    Import an Open Food facts Dump
    """

    mode = Mode.UPDATE

    def add_arguments(self, parser):
        parser.add_argument(
            '--set-mode',
            action='store',
            default=10,
            dest='mode',
            type=str,
            help='Script mode, "insert" or "update". Insert will insert the ingredients as new '
                 'entries in the database, while update will try to update them if they are '
                 'already present. Deault: insert',
        )

    def handle(self, **options):
        if options['mode'] == 'insert':
            self.mode = Mode.INSERT

        self.stdout.write('Importing entries from USDA')
        self.stdout.write(f' - {self.mode}')
        self.stdout.write('')

        usda_url = 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_json_2024-04-18.zip'

        with tempfile.TemporaryDirectory() as folder:
            folder = '/Users/roland/Entwicklung/wger/server/extras/usda'

            print(f'{folder=}')
            zip_file = os.path.join(folder, 'usda.zip')
            if os.path.exists(zip_file):
                self.stdout.write(f'Already downloaded {zip_file}, skipping download')
            else:
                self.stdout.write(f'downloading {zip_file}... (this may take a while)')
                req = requests.get(usda_url, stream=True)
                with open(zip_file, 'wb') as fid:
                    for chunk in req.iter_content(chunk_size=50 * 1024):
                        fid.write(chunk)

                self.stdout.write('download successful')

            with ZipFile(zip_file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                if not file_list:
                    raise Exception("No files found in the ZIP archive")

                first_file = file_list[0]
                self.stdout.write(f'Extracting {first_file=}')
                extracted_file_path = zip_ref.extract(first_file, path=folder)

            with open(extracted_file_path, "r") as extracted_file:
                for line in extracted_file:
                    self.process_product(line.strip().strip(','))

    def process_product(self, json_data):
        try:
            data = json.loads(json_data)
        except JSONDecodeError as e:
            # print(e)
            # print(json_data)
            # print('---------------')
            return

        name = data['description']
        fdc_id = data['fdcId']

        if not data.get('foodNutrients'):
            return

        proteins = None
        carbs = None
        fats = None
        energy = None
        for d in data['foodNutrients']:

            if not d.get("nutrient"):
                return

            nutrient = d.get("nutrient")
            nutrient_id = nutrient.get("id")

            match nutrient_id:
                case 1003:
                    proteins = float(d.get("amount"))

                case 1004:
                    carbs = float(d.get("amount"))

                case 1005:
                    fats = float(d.get("amount"))

                case 2048:
                    energy = float(d.get("amount"))

        if not all([proteins, carbs, fats, energy]):
            return

        self.stdout.write(f' - {fdc_id}')
        self.stdout.write(f' - {name}')
        self.stdout.write(f' - {proteins=}')
        self.stdout.write(f' - {carbs=}')
        self.stdout.write(f' - {fats=}')
        self.stdout.write(f' - {energy=}')

        self.stdout.write('')
        return
