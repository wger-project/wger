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
from collections import Counter

# Django
from wger.nutrition.management.commands.products import ImportProductCommand, Mode

# wger
from wger.core.models import Language
from wger.nutrition.off import extract_info_from_off

logger = logging.getLogger(__name__)


class Command(ImportProductCommand):
    """
    Import an Open Food facts Dump
    """

    completeness = 0.7

    help = 'Import an Open Food Facts dump. Please consult extras/docker/open-food-facts'

    def handle(self, **options):
        try:
            # Third Party
            from pymongo import MongoClient
        except ImportError:
            self.stdout.write('Please install pymongo, `pip install pymongo`')
            return

        self.counter = Counter()

        if options['mode'] == 'insert':
            self.mode = Mode.INSERT

        self.stdout.write('Importing entries from Open Food Facts')
        self.stdout.write(f' - {self.mode}')
        self.stdout.write('')

        client = MongoClient('mongodb://off:off-wger@127.0.0.1', port=27017)
        db = client.admin

        languages = {l.short_name: l.pk for l in Language.objects.all()}

        for product in db.products.find({'lang': {'$in': list(languages.keys())}}):
            try:
                ingredient_data = extract_info_from_off(product, languages[product['lang']])
            except KeyError as e:
                # self.stdout.write(f'--> KeyError while extracting info from OFF: {e}')
                # self.stdout.write(repr(e))
                # pprint(product)
                self.counter['skipped'] += 1
                continue

            self.handle_data(ingredient_data)

        self.stdout.write(self.style.SUCCESS('Finished!'))
        self.stdout.write(self.style.SUCCESS(str(self.counter)))
