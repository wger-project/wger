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

# wger
from wger.core.tests import powersync_base_test
from wger.measurements.models import (
    Category,
    Measurement,
)


# Pinned in test-measurement-categories.json (uuid field on the matching pk)
CATEGORY_OWNED_UUID = 'cccccccc-cccc-cccc-cccc-000000000001'  # user 'test'
CATEGORY_OTHER_UUID = 'cccccccc-cccc-cccc-cccc-0000000000aa'  # user 'admin'

# Pinned in test-measurements.json (owned via CATEGORY_OWNED_UUID)
MEASUREMENT_OWNED_UUID = 'dddddddd-dddd-dddd-dddd-000000000001'


class CategoryPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """PowerSync handlers for measurements.Category."""

    table = 'measurements_category'
    resource = Category

    pk_owned = CATEGORY_OWNED_UUID

    create_payload = {
        'id': 'cccccccc-cccc-cccc-cccc-000000000099',
        'name': 'Calf',
        'unit': 'cm',
    }
    update_payload = {
        'id': pk_owned,
        'name': 'Biceps (renamed)',
    }


class MeasurementPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """
    PowerSync handlers for measurements.Measurement. ``check_fk_ownership``
    rejects payloads pointing at another user's category.
    """

    table = 'measurements_measurement'
    resource = Measurement

    pk_owned = MEASUREMENT_OWNED_UUID

    create_payload = {
        'id': 'dddddddd-dddd-dddd-dddd-000000000099',
        'category': CATEGORY_OWNED_UUID,
        'date': '2030-01-15T10:00:00Z',
        'value': 22.5,
    }
    update_payload = {
        'id': pk_owned,
        'value': 23.5,
    }

    fk_ownership = (
        ('category', CATEGORY_OTHER_UUID),
    )
