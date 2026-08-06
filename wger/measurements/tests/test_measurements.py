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

# Standard Library
import json
from decimal import Decimal

# Django
from django.contrib.auth.models import User
from django.db import (
    IntegrityError,
    transaction,
)

# Django
from django.urls import reverse

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType


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


class MeasurementLeafOnlyTestCase(WgerTestCase):
    """
    Measurements can only be added to leaf categories, not to group parents
    """

    parent_id = 'cccccccc-cccc-cccc-cccc-000000000003'  # user 'test', no measurements

    def test_measurement_on_parent_category_rejected(self):
        self.user_login('test')
        parent = Category.objects.get(pk=self.parent_id)
        Category.objects.create(
            user=parent.user,
            name='Systolic',
            unit='mmHg',
            parent=parent,
        )

        response = self.client.post(
            reverse('measurement-list'),
            {
                'category': self.parent_id,
                'date': '2021-08-12',
                'value': 120,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('category', response.data)

    def test_measurement_on_group_type_rejected(self):
        """
        A group type is a container even while it has no children yet
        """
        self.user_login('test')
        Category.objects.filter(pk=self.parent_id).update(
            metric_type=MetricType.BLOOD_PRESSURE,
        )

        response = self.client.post(
            reverse('measurement-list'),
            {
                'category': self.parent_id,
                'date': '2021-08-12',
                'value': 120,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('category', response.data)


class MeasurementUnitTestCase(WgerTestCase):
    """
    Per-entry units in extra_data
    """

    # kg entry in the official body weight category of user 'test'
    entry_pk = '11111111-1111-1111-1111-000000000001'  # 77 kg

    def test_unit_falls_back_to_category(self):
        """
        Test that entries without a stamped unit use the category unit
        """
        entry = Measurement.objects.get(pk=self.entry_pk)

        self.assertEqual(entry.extra_data, {})
        self.assertEqual(entry.unit, 'kg')

    def test_unit_from_extra_data(self):
        """
        Test that a stamped unit wins over the category unit
        """
        entry = Measurement.objects.get(pk=self.entry_pk)
        entry.extra_data = {'unit': 'lb'}

        self.assertEqual(entry.unit, 'lb')

    def test_value_in_same_unit(self):
        """
        Test that no conversion happens for the entry's own unit
        """
        entry = Measurement.objects.get(pk=self.entry_pk)

        self.assertEqual(entry.value_in('kg'), Decimal('77.00'))

    def test_value_in_converts(self):
        """
        Test the conversion between kg and lb
        """
        entry = Measurement.objects.get(pk=self.entry_pk)

        self.assertEqual(entry.value_in('lb'), Decimal('169.76'))

        entry.extra_data = {'unit': 'lb'}
        self.assertEqual(entry.value_in('kg'), Decimal('34.93'))

    def test_value_in_rejects_other_units(self):
        """
        Test that only weight units can be converted
        """
        # a measurement in the 'Biceps' category of user 'test', unit cm
        entry = Measurement.objects.get(pk='dddddddd-dddd-dddd-dddd-000000000001')

        self.assertEqual(entry.value_in('cm'), entry.value)
        with self.assertRaises(ValueError):
            entry.value_in('kg')


class MeasurementValueLimitsTestCase(WgerTestCase):
    """
    The range a value may be in follows the metric type of its category
    """

    body_weight_id = 'cccccccc-cccc-cccc-cccc-0000000000b0'  # user 'test', kg
    custom_id = 'cccccccc-cccc-cccc-cccc-000000000001'  # user 'test', cm

    def setUp(self):
        super().setUp()
        self.user_login('test')
        self.url = reverse('measurement-list')

    def add_entry(self, category_id, value, extra_data=None):
        return self.client.post(
            self.url,
            {
                'category': str(category_id),
                'date': '2023-05-01T12:00:00Z',
                'value': value,
                'extra_data': extra_data or {},
            },
            content_type='application/json',
        )

    def create_category(self, metric_type, unit):
        return Category.objects.create(
            user=User.objects.get(username='test'),
            name=metric_type,
            unit=unit,
            metric_type=metric_type,
        )

    def test_daily_step_count(self):
        """
        Test that a daily step total is accepted
        """
        category = self.create_category(MetricType.STEPS, 'count')

        self.assertEqual(self.add_entry(category.pk, 11000).status_code, 201)

    def test_value_above_limit(self):
        """
        Test that a value above the limit of its metric type is rejected
        """
        category = self.create_category(MetricType.STEPS, 'count')

        response = self.add_entry(category.pk, 150000)

        self.assertEqual(response.status_code, 400)
        self.assertIn('value', response.data)

    def test_value_below_limit(self):
        """
        Test that a value below the limit of its metric type is rejected
        """
        category = self.create_category(MetricType.HEART_RATE, 'bpm')

        response = self.add_entry(category.pk, 5)

        self.assertEqual(response.status_code, 400)
        self.assertIn('value', response.data)

    def test_body_weight_limits_per_unit(self):
        """
        Test that the body weight bounds are resolved in the entry's own unit
        """
        self.assertEqual(self.add_entry(self.body_weight_id, 700, {'unit': 'lb'}).status_code, 201)

        response = self.add_entry(self.body_weight_id, 700, {'unit': 'kg'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('value', response.data)

    def test_custom_category_limited_by_column(self):
        """
        Test that a free-form category is only bounded by the column itself
        """
        self.assertEqual(self.add_entry(self.custom_id, 50000).status_code, 201)
        self.assertEqual(self.add_entry(self.custom_id, 1000000).status_code, 400)

    def test_limits_on_update(self):
        """
        Test that updating a value validates it as well
        """
        entry = Measurement.objects.filter(category_id=self.body_weight_id).first()

        response = self.client.patch(
            reverse('measurement-detail', kwargs={'pk': entry.pk}),
            {'value': 700},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('value', response.data)

    def test_editing_an_entry_outside_the_limits(self):
        """
        Test that a stored value outside the limits does not block other edits
        """
        entry = Measurement.objects.filter(category_id=self.body_weight_id).first()
        Measurement.objects.filter(pk=entry.pk).update(value=550)

        response = self.client.patch(
            reverse('measurement-detail', kwargs={'pk': entry.pk}),
            {'notes': 'Wrong unit'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.notes, 'Wrong unit')
        self.assertEqual(entry.value, Decimal(550))

    def test_correcting_an_entry_outside_the_limits(self):
        """
        Test that such an entry can be corrected, but only to a valid value
        """
        entry = Measurement.objects.filter(category_id=self.body_weight_id).first()
        Measurement.objects.filter(pk=entry.pk).update(value=550)
        url = reverse('measurement-detail', kwargs={'pk': entry.pk})

        self.assertEqual(
            self.client.patch(url, {'value': 600}, content_type='application/json').status_code,
            400,
        )
        self.assertEqual(
            self.client.patch(url, {'value': 80}, content_type='application/json').status_code,
            200,
        )

    def test_editing_an_entry_whose_stored_unit_is_unknown(self):
        """
        Test that a stored unit outside kg and lb does not block other edits
        """
        entry = Measurement.objects.filter(category_id=self.body_weight_id).first()
        Measurement.objects.filter(pk=entry.pk).update(extra_data={'unit': 'st'})

        response = self.client.patch(
            reverse('measurement-detail', kwargs={'pk': entry.pk}),
            {'notes': 'Stones'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)


class MeasurementExtraDataApiTestCase(WgerTestCase):
    """
    extra_data over the measurement API
    """

    def setUp(self):
        super().setUp()
        self.user_login('test')
        self.url = reverse('measurement-list')

    def test_extra_data_roundtrip(self):
        """
        Test that extra_data can be set and read over the API
        """
        response = self.client.post(
            self.url,
            {
                'category': 'cccccccc-cccc-cccc-cccc-0000000000b0',
                'date': '2023-05-01T12:00:00Z',
                'value': 180,
                'extra_data': {'unit': 'lb'},
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['extra_data'], {'unit': 'lb'})
        self.assertEqual(Measurement.objects.get(pk=response.data['id']).unit, 'lb')

    def test_extra_data_size_bound(self):
        """
        Test that an oversized extra_data blob is refused

        The column is an unbounded JSONField, so this is the only thing keeping
        a client from pushing arbitrarily large blobs into the table
        """
        response = self.client.post(
            self.url,
            {
                'category': 'cccccccc-cccc-cccc-cccc-0000000000b0',
                'date': '2023-05-01T12:00:00Z',
                'value': 180,
                'extra_data': {'unit': 'lb', 'blob': 'x' * 1000},
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('extra_data', response.data)

    def test_extra_data_size_bound_leaves_room(self):
        """
        Test that a large but sane extra_data payload still passes

        The importer's provenance is ~200 bytes; the bound is headroom, not a
        fitted cap
        """
        response = self.client.post(
            self.url,
            {
                'category': 'cccccccc-cccc-cccc-cccc-0000000000b0',
                'date': '2023-05-01T12:00:00Z',
                'value': 180,
                'extra_data': {'unit': 'lb', 'source_name': 'x' * 900},
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)

    def test_invalid_body_weight_unit(self):
        """
        Test that body weight entries only accept kg and lb as unit
        """
        response = self.client.post(
            self.url,
            {
                'category': 'cccccccc-cccc-cccc-cccc-0000000000b0',
                'date': '2023-05-01T12:00:00Z',
                'value': 180,
                'extra_data': {'unit': 'stone'},
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('extra_data', response.data)

    def test_moving_an_entry_with_a_foreign_unit(self):
        """
        Test that an entry cannot be moved into the body weight category while
        it carries a unit that category does not support
        """
        entry = self.client.post(
            self.url,
            {
                'category': 'cccccccc-cccc-cccc-cccc-000000000003',
                'date': '2023-05-01T12:00:00Z',
                'value': 42,
                'extra_data': {'unit': 'rods to the hogshead'},
            },
            content_type='application/json',
        )

        response = self.client.patch(
            reverse('measurement-detail', kwargs={'pk': entry.data['id']}),
            {'category': 'cccccccc-cccc-cccc-cccc-0000000000b0'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('extra_data', response.data)

    def test_custom_category_unit_free(self):
        """
        Test that custom categories accept any unit in extra_data
        """
        response = self.client.post(
            self.url,
            {
                'category': 'cccccccc-cccc-cccc-cccc-000000000003',
                'date': '2023-05-01T12:00:00Z',
                'value': 42,
                'extra_data': {'unit': 'rods to the hogshead'},
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)


class AggregateBoundValidationTestCase(WgerTestCase):
    """
    The min and max of a daily aggregate have to be numbers: the chart
    aggregate casts them in SQL, and a string breaks every read of the category
    """

    category_id = 'cccccccc-cccc-cccc-cccc-000000000002'

    def setUp(self):
        super().setUp()
        self.user_login('test')

    def post(self, extra_data):
        return self.client.post(
            reverse('measurement-list'),
            json.dumps(
                {
                    'category': self.category_id,
                    'date': '2026-05-04T08:00:00Z',
                    'value': '70.00',
                    'extra_data': extra_data,
                }
            ),
            content_type='application/json',
        )

    def test_a_numeric_bound_is_accepted(self):
        response = self.post({'min': 48, 'max': 165.5})

        self.assertEqual(response.status_code, 201, response.data)

    def test_a_bound_written_as_a_string_is_refused(self):
        for extra_data in ({'min': '48'}, {'max': 'abc'}):
            response = self.post(extra_data)

            self.assertEqual(response.status_code, 400)
            self.assertIn('extra_data', response.data)

    def test_extra_data_without_bounds_is_untouched(self):
        self.assertEqual(self.post({'unit': 'kg', 'source_name': 'Withings'}).status_code, 201)
