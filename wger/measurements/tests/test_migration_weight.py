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
import datetime
import uuid
from decimal import Decimal
from importlib import import_module
from types import SimpleNamespace

# Django
from django.test import SimpleTestCase


migration = import_module('wger.measurements.migrations.0007_migrate_weight')

USER_ID = 42
CATEGORY_ID = uuid.UUID('cccccccc-cccc-cccc-cccc-000000000001')


def entry(weight, entry_uuid=None, date=datetime.date(2026, 5, 4)):
    return SimpleNamespace(
        uuid=entry_uuid or uuid.uuid4(),
        user_id=USER_ID,
        date=date,
        weight=Decimal(str(weight)),
    )


class OfficialCategoryTestCase(SimpleTestCase):
    """
    Test the category every user gets in the weight data migration
    """

    def test_the_category_is_the_official_body_weight_one(self):
        fields = migration.official_category(USER_ID, 'kg')

        self.assertEqual(fields['user_id'], USER_ID)
        self.assertEqual(fields['metric_type'], 'body_weight')
        self.assertTrue(fields['is_official'])
        self.assertEqual(fields['name'], 'Body weight')

    def test_it_is_created_in_the_unit_the_user_weighed_in(self):
        self.assertEqual(migration.official_category(USER_ID, 'lb')['unit'], 'lb')
        self.assertEqual(migration.official_category(USER_ID, 'kg')['unit'], 'kg')

    def test_a_profile_without_a_unit_falls_back_to_kg(self):
        # Also the branch for a user with no profile at all, who is looked up
        # with no unit to go by
        self.assertEqual(migration.official_category(USER_ID, None)['unit'], 'kg')
        self.assertEqual(migration.official_category(USER_ID, '')['unit'], 'kg')


class MeasurementFromTestCase(SimpleTestCase):
    """
    Test what a weight entry becomes in the weight data migration
    """

    def test_the_entry_keeps_its_identity(self):
        # Clients synchronise weight entries by uuid, so the row they know has
        # to keep it
        stored = uuid.uuid4()

        fields = migration.measurement_from(entry(80, stored), CATEGORY_ID, 'kg')

        self.assertEqual(fields['id'], stored)

    def test_value_and_date_are_carried_over(self):
        day = datetime.date(2021, 12, 10)

        fields = migration.measurement_from(entry(80.5, date=day), CATEGORY_ID, 'kg')

        self.assertEqual(fields['value'], Decimal('80.5'))
        self.assertEqual(fields['date'], day)
        self.assertEqual(fields['category_id'], CATEGORY_ID)

    def test_the_entry_is_the_users_own_reading(self):
        # Not an import and not calculated: it is what they typed
        self.assertEqual(migration.measurement_from(entry(80), CATEGORY_ID, 'kg')['source'], 'user')

    def test_the_unit_of_the_category_is_stamped_on_the_entry(self):
        # A value means nothing without it: the column is a bare number, and a
        # category can hold entries in either unit from here on
        fields = migration.measurement_from(entry(176.37), CATEGORY_ID, 'lb')

        self.assertEqual(fields['extra_data'], {'unit': 'lb'})

    def test_the_value_is_not_converted(self):
        # 176.37 lb are stored as 176.37, in lb, rather than as 80 kg
        fields = migration.measurement_from(entry(176.37), CATEGORY_ID, 'lb')

        self.assertEqual(fields['value'], Decimal('176.37'))
