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

# Django
from django.contrib.auth.models import User

# Third Party
from rest_framework import status

# wger
from wger.core.tests import powersync_base_test
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType


# Pinned in test-measurement-categories.json (uuid field on the matching pk)
CATEGORY_OWNED_UUID = 'cccccccc-cccc-cccc-cccc-000000000001'  # user 'test'
CATEGORY_OTHER_UUID = 'cccccccc-cccc-cccc-cccc-0000000000aa'  # user 'admin'

# Pinned in test-measurements.json (owned via CATEGORY_OWNED_UUID)
MEASUREMENT_OWNED_UUID = 'dddddddd-dddd-dddd-dddd-000000000001'


class CategoryPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """
    PowerSync handlers for measurements.Category. ``check_fk_ownership``
    rejects payloads pointing at another user's category via ``parent``.
    """

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

    fk_ownership = (('parent', CATEGORY_OTHER_UUID),)


class TypedCategoryPowerSyncTestCase(powersync_base_test.PowerSyncBaseTestCase):
    """
    Typed categories created by an offline client.

    The client derives the same keys the server would, so its pushes converge on
    the rows that are already there instead of duplicating them.
    """

    table = 'measurements_category'
    resource = Category

    def setUp(self):
        super().setUp()
        self.authenticate()
        self.user = User.objects.get(username=self.user_access)

    def push_category(self, metric_type, **data):
        payload = {
            'id': str(Category.deterministic_id(self.user.pk, metric_type)),
            'name': 'Blood pressure',
            'unit': 'mmHg',
            'metric_type': metric_type,
            **data,
        }
        return self.push('PUT', payload)

    def test_group_push_creates_components(self):
        """
        A group pushed by the client arrives with its components
        """
        response = self.push_category(MetricType.BLOOD_PRESSURE)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(
            Category.objects.filter(
                user=self.user,
                parent__metric_type=MetricType.BLOOD_PRESSURE,
            ).count(),
            2,
        )

    def test_component_push_matches_the_created_component(self):
        """
        A component the client created offline lands on the existing row
        """
        self.push_category(MetricType.BLOOD_PRESSURE)
        count_before = Category.objects.count()

        response = self.push_category(
            MetricType.BLOOD_PRESSURE_SYSTOLIC,
            name='Systolic',
            parent=str(Category.deterministic_id(self.user.pk, MetricType.BLOOD_PRESSURE)),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(Category.objects.count(), count_before)

    def test_duplicate_typed_category_refused(self):
        """
        A second category of the same type is refused permanently
        """
        self.push_category(MetricType.STEPS, name='Steps', unit='count')
        count_before = Category.objects.count()

        response = self.push(
            'PUT',
            {
                'id': 'cccccccc-cccc-cccc-cccc-000000000098',
                'name': 'Steps again',
                'unit': 'count',
                'metric_type': MetricType.STEPS,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertTrue(response.json().get('error'), response.content)
        self.assertEqual(Category.objects.count(), count_before)


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

    fk_ownership = (('category', CATEGORY_OTHER_UUID),)

    def test_create_decodes_extra_data_string(self):
        """
        PowerSync clients store JSON columns as text; the handler decodes the
        string before validation
        """
        self.authenticate()
        payload = {**self.create_payload, 'extra_data': '{"unit": "kg"}'}
        response = self.push('PUT', payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(response.json(), {'status': 'ok!'})
        measurement = Measurement.objects.get(pk=payload['id'])
        self.assertEqual(measurement.extra_data, {'unit': 'kg'})

    def test_create_rejects_malformed_extra_data(self):
        """
        A malformed JSON string passes through undecoded and is rejected by the
        serializer instead of crashing the handler
        """
        self.authenticate()
        payload = {**self.create_payload, 'extra_data': '{not json'}
        response = self.push('PUT', payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json().get('error'), response.content)
        self.assertFalse(Measurement.objects.filter(pk=payload['id']).exists())
