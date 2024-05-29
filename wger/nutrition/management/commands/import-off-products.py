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

# Third Party
import requests
from pymongo import MongoClient

# wger
from wger.core.models import Language
from wger.nutrition.management.products import (
    ImportProductCommand,
    Mode,
)
from wger.nutrition.off import extract_info_from_off


logger = logging.getLogger(__name__)


class Command(ImportProductCommand):
    """
    Import an Open Food facts Dump
    """

    help = 'Import an Open Food Facts dump. Please consult extras/docker/open-food-facts'

    deltas_base_url = 'https://static.openfoodfacts.org/data/delta/'
    full_off_dump_url = 'https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz'

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--jsonl',
            action='store_true',
            default=False,
            dest='use_jsonl',
            help=(
                'Use the JSONL dump of the Open Food Facts database.'
                '(this option does not require mongo)'
            ),
        )

        parser.add_argument(
            '--delta-updates',
            action='store_true',
            default=False,
            dest='delta_updates',
            help='Downloads and imports the most recent delta file',
        )

    def import_mongo(self, languages: dict[str:int]):
        client = MongoClient('mongodb://off:off-wger@127.0.0.1', port=27017)
        db = client.admin
        for product in db.products.find({'lang': {'$in': list(languages.keys())}}):
            try:
                ingredient_data = extract_info_from_off(product, languages[product['lang']])
            except (KeyError, ValueError) as e:
                # self.stdout.write(f'--> KeyError while extracting info from OFF: {e}')
                self.counter['skipped'] += 1
            else:
                self.process_ingredient(ingredient_data)

    def import_daily_delta(self, languages: dict[str:int], destination: str):
        download_folder, tmp_folder = self.get_download_folder(destination)

        # Fetch the index page with requests and read the result
        index_url = self.deltas_base_url + 'index.txt'
        req = requests.get(index_url)
        index_content = req.text
        newest_entry = index_content.split('\n')[0]

        file_path = os.path.join(download_folder, newest_entry)

        # Fetch the newest entry and extract the contents
        delta_url = self.deltas_base_url + newest_entry
        self.download_file(delta_url, file_path)

        self.stdout.write('Start processing...')
        for entry in self.iterate_gz_file_contents(file_path, list(languages.keys())):
            try:
                ingredient_data = extract_info_from_off(entry, languages[entry['lang']])
            except (KeyError, ValueError) as e:
                self.stdout.write(
                    f'--> {ingredient_data.remote_id=} Error while extracting info from OFF: {e}'
                )
                self.counter['skipped'] += 1
            else:
                self.process_ingredient(ingredient_data)

        if tmp_folder:
            self.stdout.write(f'Removing temporary folder {download_folder}')
            tmp_folder.cleanup()

    def import_full_dump(self, languages: dict[str:int], destination: str):
        download_folder, tmp_folder = self.get_download_folder(destination)

        file_path = os.path.join(download_folder, os.path.basename(self.full_off_dump_url))
        self.download_file(self.full_off_dump_url, file_path)

        self.stdout.write('Start processing...')
        for entry in self.iterate_gz_file_contents(file_path, list(languages.keys())):
            try:
                ingredient_data = extract_info_from_off(entry, languages[entry['lang']])
            except (KeyError, ValueError) as e:
                self.stdout.write(f'--> Error while extracting info from OFF: {e}')
                self.counter['skipped'] += 1
            else:
                self.process_ingredient(ingredient_data)

        if tmp_folder:
            self.stdout.write(f'Removing temporary folder {download_folder}')
            tmp_folder.cleanup()

    def handle(self, **options):
        try:
            # Third Party
            from pymongo import MongoClient
        except ImportError:
            self.stdout.write('Please install pymongo, `pip install pymongo`')
            return

        if options['mode'] == 'insert':
            self.mode = Mode.INSERT

        self.stdout.write('Importing entries from Open Food Facts')
        self.stdout.write(f' - {self.mode}')
        if options['delta_updates']:
            self.stdout.write(f' - importing only delta updates')
        elif options['use_jsonl']:
            self.stdout.write(f' - importing the full dump')
        else:
            self.stdout.write(f' - importing from mongo')
        self.stdout.write('')

        languages = {lang.short_name: lang.pk for lang in Language.objects.all()}
        if options['delta_updates']:
            self.import_daily_delta(languages, options['folder'])
        elif options['use_jsonl']:
            self.import_full_dump(languages, options['folder'])
        else:
            self.import_mongo(languages)

        self.stdout.write(self.style.SUCCESS('Finished!'))
        self.stdout.write(self.style.SUCCESS(str(self.counter)))
