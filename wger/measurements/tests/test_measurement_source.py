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
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests import powersync_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType
from wger.measurements.models.measurement import MeasurementSource


EXTERNAL_ID = 'eeeeeeee-eeee-eeee-eeee-0000000000d1'
DEVICE_EXTRA_DATA = {'v': 1, 'vendor': 'acme', 'model': 'band-2', 'kind': 'hr'}


def create_heart_rate_category(user: User) -> Category:
    return Category.objects.create(
        user=user,
        name='Heart rate',
        unit='bpm',
        metric_type=MetricType.HEART_RATE,
    )


class DeviceSourceApiTestCase(WgerTestCase):
    """
    The generic `device` source: wearables and sensors writing on behalf of the user
    """

    def setUp(self):
        super().setUp()
        self.user_login('test')
        self.category = create_heart_rate_category(User.objects.get(username='test'))
        self.url = reverse('measurement-list')

    def post(self, **fields):
        payload = {
            'category': str(self.category.pk),
            'date': '2026-10-08T07:30:00Z',
            'value': 72,
            'source': 'device',
            **fields,
        }
        return self.client.post(self.url, payload, content_type='application/json')

    def test_create_heart_rate_with_device_source(self):
        response = self.post(external_id=EXTERNAL_ID, extra_data=DEVICE_EXTRA_DATA)

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['source'], 'device')
        entry = Measurement.objects.get(pk=response.data['id'])
        self.assertEqual(entry.source, MeasurementSource.DEVICE)
        self.assertEqual(entry.extra_data, DEVICE_EXTRA_DATA)

    def test_device_source_dedupes_on_external_id(self):
        self.assertEqual(self.post(external_id=EXTERNAL_ID).status_code, 201)

        response = self.post(external_id=EXTERNAL_ID)

        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(
            Measurement.objects.filter(
                category=self.category,
                source=MeasurementSource.DEVICE,
                external_id=EXTERNAL_ID,
            ).count(),
            1,
        )

    def test_device_source_does_not_collide_with_other_sources(self):
        """
        The external id is only unique per source
        """
        self.assertEqual(self.post(external_id=EXTERNAL_ID, source='apple').status_code, 201)

        self.assertEqual(self.post(external_id=EXTERNAL_ID).status_code, 201)

    def test_device_source_respects_heart_rate_limits(self):
        for value in (25, 260):
            with self.subTest(value=value):
                response = self.post(value=value)

                self.assertEqual(response.status_code, 400)
                self.assertIn('value', response.data)

        self.assertFalse(Measurement.objects.filter(category=self.category).exists())

    def test_filter_by_source_device(self):
        self.post(value=70)
        self.post(value=71, source='user')

        response = self.client.get(
            self.url, {'category': str(self.category.pk), 'source': 'device'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([e['source'] for e in response.data['results']], ['device'])

    def test_unknown_source_is_still_refused(self):
        response = self.post(source='wearable')

        self.assertEqual(response.status_code, 400)
        self.assertIn('source', response.data)


class DeviceSourcePowerSyncTestCase(powersync_base_test.PowerSyncBaseTestCase):
    """
    The PowerSync upload handler takes the `device` source as well
    """

    table = 'measurements_measurement'
    resource = Measurement

    def test_powersync_upload_accepts_device_source(self):
        self.authenticate()
        category = create_heart_rate_category(User.objects.get(username=self.user_access))
        payload = {
            'id': 'dddddddd-dddd-dddd-dddd-0000000000d9',
            'category': str(category.pk),
            'date': '2030-01-15T10:00:00Z',
            'value': 64,
            'source': 'device',
            'external_id': EXTERNAL_ID,
            'extra_data': '{"v": 1, "vendor": "acme", "model": "band-2"}',
        }

        response = self.push('PUT', payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(response.json(), {'status': 'ok!'})
        entry = Measurement.objects.get(pk=payload['id'])
        self.assertEqual(entry.source, MeasurementSource.DEVICE)
        self.assertEqual(entry.extra_data['vendor'], 'acme')
