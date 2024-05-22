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

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--jsonl',
            action='store_true',
            default=False,
            dest='usejsonl',
            help='Use the JSONL dump of the Open Food Facts database.'
            '(this option does not require mongo)'
        )

    def products_jsonl(self,languages,completeness):
        import json
        import requests
        from gzip import GzipFile
        off_url='https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz'
        download_dir=os.path.expanduser('~/.cache/off_cache')
        os.makedirs(download_dir,exist_ok=True)
        gzipdb=os.path.join(download_dir,os.path.basename(off_url))
        if os.path.exists(gzipdb):
            self.stdout.write(f'Already downloaded {gzipdb}, skipping download')
        else:
            self.stdout.write(f'downloading {gzipdb}... (this may take a while)')
            req=requests.get(off_url,stream=True)
            with open(gzipdb,'wb') as fid:
                for chunk in req.iter_content(chunk_size=50*1024):
                    fid.write(chunk)
        with GzipFile(gzipdb,'rb') as gzid:
            for line in gzid:
                try:
                    product=json.loads(line)
                    if product['completeness'] < completeness:
                        continue
                    if not product['lang'] in languages:
                        continue
                    yield product
                except:
                    self.stdout.write(f' Error parsing and/or filtering  json record, skipping')
                    continue

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
        self.stdout.write('')

        client = MongoClient('mongodb://off:off-wger@127.0.0.1', port=27017)
        db = client.admin

        languages = {lang.short_name: lang.pk for lang in Language.objects.all()}

        for product in db.products.find({'lang': {'$in': list(languages.keys())}}):
            try:
                ingredient_data = extract_info_from_off(product, languages[product['lang']])
            except KeyError as e:
                # self.stdout.write(f'--> KeyError while extracting info from OFF: {e}')
                # self.stdout.write(repr(e))
                # pprint(product)
                self.counter['skipped'] += 1
            else:
                self.handle_data(ingredient_data)

        self.stdout.write(self.style.SUCCESS('Finished!'))
        self.stdout.write(self.style.SUCCESS(str(self.counter)))
