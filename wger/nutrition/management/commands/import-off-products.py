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
import logging
from collections import Counter

# Django
from django.core.management.base import BaseCommand

# wger
from wger.core.models import Language
from wger.nutrition.models import Ingredient
from wger.nutrition.off import extract_info_from_off


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
    bulk_size = 500
    completeness = 0.7

    help = 'Import an Open Food Facts dump. Please consult extras/docker/open-food-facts'

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
        parser.add_argument(
            '--completeness',
            action='store',
            default=0.7,
            dest='completeness',
            type=float,
            help='Completeness threshold for importing the products. Products in OFF have '
            'completeness score that ranges from 0 to 1.1. Default: 0.7',
        )

    def handle(self, **options):
        try:
            # Third Party
            from pymongo import MongoClient
        except ImportError:
            self.stdout.write('Please install pymongo, `pip install pymongo`')
            return

        if options['mode'] == 'insert':
            self.mode = Mode.INSERT

        if options['completeness'] < 0 or options['completeness'] > 1.1:
            self.stdout.write('Completeness must be between 0 and 1.1')
            return
        self.completeness = options['completeness']

        self.stdout.write('Importing entries from Open Food Facts')
        self.stdout.write(f' - Completeness threshold: {self.completeness}')
        self.stdout.write(f' - {self.mode}')
        self.stdout.write('')

        client = MongoClient('mongodb://off:off-wger@127.0.0.1', port=27017)
        db = client.admin

        languages = {l.short_name: l.pk for l in Language.objects.all()}

        bulk_update_bucket = []
        counter = Counter()

        for product in db.products.find(
            {'lang': {'$in': list(languages.keys())}, 'completeness': {'$gt': self.completeness}}
        ):
            try:
                ingredient_data = extract_info_from_off(product, languages[product['lang']])
            except KeyError as e:
                # self.stdout.write(f'--> KeyError while extracting info from OFF: {e}')
                # self.stdout.write(
                #    '***********************************************************************************************')
                # self.stdout.write(
                #    '***********************************************************************************************')
                # self.stdout.write(
                #    '***********************************************************************************************')
                # pprint(product)
                # self.stdout.write(f'--> Product: {product}')
                counter['skipped'] += 1
                continue

            # Some products have no name or name is too long, skipping
            if not ingredient_data.name:
                # self.stdout.write('--> Ingredient has no name field')
                counter['skipped'] += 1
                continue

            if not ingredient_data.common_name:
                # self.stdout.write('--> Ingredient has no common name field')
                counter['skipped'] += 1
                continue

            #
            # Add entries as new products
            if self.mode == Mode.INSERT:
                bulk_update_bucket.append(Ingredient(**ingredient_data.dict()))
                if len(bulk_update_bucket) > self.bulk_size:
                    try:
                        Ingredient.objects.bulk_create(bulk_update_bucket)
                        self.stdout.write('***** Bulk adding products *****')
                    except Exception as e:
                        self.stdout.write(
                            '--> Error while saving the product bucket. Saving individually'
                        )
                        self.stdout.write(e)

                        # Try saving the ingredients individually as most will be correct
                        for ingredient in bulk_update_bucket:
                            try:
                                ingredient.save()

                            # ¯\_(ツ)_/¯
                            except Exception as e:
                                self.stdout.write('--> Error while saving the product individually')
                                self.stdout.write(e)

                    counter['new'] += self.bulk_size
                    bulk_update_bucket = []

            # Update existing entries
            else:
                try:
                    # Update an existing product (look-up key is the code) or create a new
                    # one. While this might not be the most efficient query (there will always
                    # be a SELECT first), it's ok because this script is run very rarely.
                    obj, created = Ingredient.objects.update_or_create(
                        code=ingredient_data.code,
                        defaults=ingredient_data.dict(),
                    )

                    if created:
                        counter['new'] += 1
                        # self.stdout.write('-> added to the database')
                    else:
                        counter['edited'] += 1
                        # self.stdout.write('-> updated')

                except Exception as e:
                    self.stdout.write('--> Error while performing update_or_create')
                    self.stdout.write(str(e))
                    counter['error'] += 1
                    continue

        self.stdout.write(self.style.SUCCESS('Finished!'))
        self.stdout.write(self.style.SUCCESS(str(counter)))
