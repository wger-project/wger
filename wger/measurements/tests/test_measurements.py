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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Django
from django.db import (
    IntegrityError,
    transaction,
)

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.measurements.models import Measurement


class MeasurementsApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the measurements endpoint
    """

    pk = 'dddddddd-dddd-dddd-dddd-000000000001'
    resource = Measurement
    private_resource = True
    data = {
        'category': 'cccccccc-cccc-cccc-cccc-000000000002',
        'date': '2021-08-12',
        'value': 99.99,
    }


class ExternalMeasurementConstraintTestCase(WgerTestCase):
    """
    The (category, source, external_id) uniqueness that keeps re-imports idempotent.
    """

    category_id = 'cccccccc-cccc-cccc-cccc-000000000002'
    external_id = 'eeeeeeee-eeee-eeee-eeee-000000000001'

    def _create(self, **kwargs):
        defaults = {
            'category_id': self.category_id,
            'value': 42,
            'source': 'apple',
            'external_id': self.external_id,
        }
        defaults.update(kwargs)
        return Measurement.objects.create(**defaults)

    def test_duplicate_external_record_rejected(self):
        self._create()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self._create()

    def test_null_external_id_allows_duplicates(self):
        before = Measurement.objects.count()
        self._create(external_id=None)
        self._create(external_id=None)
        self.assertEqual(Measurement.objects.count(), before + 2)
