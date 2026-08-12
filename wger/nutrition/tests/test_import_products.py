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
import gzip
import json
import os
import tempfile

# Django
from django.core.management import call_command

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.consts import OFF_FULL_DUMP_URL
from wger.nutrition.models import Ingredient


def off_product(code: str, name: str, lang: str = 'de', **overrides) -> dict:
    """
    A minimal product as it appears in the Open Food Facts dump
    """
    product = {
        'code': code,
        'lang': lang,
        'product_name': name,
        'nutriments': {
            'energy-kcal_100g': 600,
            'proteins_100g': 10,
            'carbohydrates_100g': 30,
            'fat_100g': 40,
        },
    }
    product.update(overrides)
    return product


class ImportOffProductsTestCase(WgerTestCase):
    """
    Tests importing a full Open Food Facts dump

    The dump is written to a folder passed with --folder, so the command
    finds the file in place and never downloads anything.
    """

    def run_import(self, lines: list, **options) -> str:
        """
        Writes the lines as a gzipped dump and runs the import over it
        """
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, os.path.basename(OFF_FULL_DUMP_URL))
            with gzip.open(path, 'wt') as dump:
                for line in lines:
                    dump.write(line if isinstance(line, str) else json.dumps(line))
                    dump.write('\n')

            call_command('import-off-products', '--jsonl', folder=folder, **options)
            return folder

    def test_products_are_imported(self):
        count_before = Ingredient.objects.count()

        self.run_import([off_product('111', 'Imported product')])

        self.assertEqual(Ingredient.objects.count(), count_before + 1)
        ingredient = Ingredient.objects.get(remote_id='111')
        self.assertEqual(ingredient.name, 'Imported product')
        self.assertEqual(ingredient.energy, 600)

    def test_existing_products_are_updated(self):
        self.run_import([off_product('222', 'First name')])
        count_after_first = Ingredient.objects.count()

        self.run_import([off_product('222', 'Second name')])

        self.assertEqual(Ingredient.objects.count(), count_after_first)
        self.assertEqual(Ingredient.objects.get(remote_id='222').name, 'Second name')

    def test_products_in_other_languages_are_skipped(self):
        count_before = Ingredient.objects.count()

        self.run_import([off_product('333', 'Klingon food', lang='tlh')])

        self.assertEqual(Ingredient.objects.count(), count_before)

    def test_malformed_json_does_not_abort_the_run(self):
        count_before = Ingredient.objects.count()

        self.run_import(
            [
                off_product('444', 'Before the broken line'),
                'this is not json',
                off_product('555', 'After the broken line'),
            ]
        )

        self.assertEqual(Ingredient.objects.count(), count_before + 2)
        self.assertTrue(Ingredient.objects.filter(remote_id='555').exists())

    def test_incomplete_product_does_not_abort_the_run(self):
        """
        Products missing required keys are skipped, the import continues
        """
        count_before = Ingredient.objects.count()
        incomplete = off_product('666', 'No nutriments')
        del incomplete['nutriments']

        self.run_import(
            [
                incomplete,
                off_product('777', 'Complete product'),
            ]
        )

        self.assertEqual(Ingredient.objects.count(), count_before + 1)
        self.assertTrue(Ingredient.objects.filter(remote_id='777').exists())

    def test_implausible_product_does_not_abort_the_run(self):
        """
        Products failing the sanity checks are skipped, the import continues
        """
        count_before = Ingredient.objects.count()
        implausible = off_product('888', 'Impossible macros')
        implausible['nutriments']['proteins_100g'] = 100
        implausible['nutriments']['carbohydrates_100g'] = 100
        implausible['nutriments']['fat_100g'] = 100

        self.run_import(
            [
                implausible,
                off_product('999', 'Sane product'),
            ]
        )

        self.assertEqual(Ingredient.objects.count(), count_before + 1)
        self.assertTrue(Ingredient.objects.filter(remote_id='999').exists())

    def test_non_numeric_nutriments_do_not_abort_the_run(self):
        """
        The dump is user-generated, a string where a number belongs must not
        take down the whole import
        """
        count_before = Ingredient.objects.count()
        broken = off_product('1000', 'String nutriments')
        broken['nutriments']['proteins_100g'] = 'a lot'

        self.run_import(
            [
                broken,
                off_product('1001', 'Sane product'),
            ]
        )

        self.assertEqual(Ingredient.objects.count(), count_before + 1)
        self.assertTrue(Ingredient.objects.filter(remote_id='1001').exists())
