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
import uuid
from decimal import Decimal

# Django
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType
from wger.utils.api_token import create_token
from wger.weight.api.serializers import (
    SIGNED_LONG_MAX,
    compatible_weight_entry_id,
)


def measurement_for_compatible_id(user, compatible_id):
    matches = [
        measurement
        for measurement in Measurement.objects.filter(category__user=user)
        if compatible_weight_entry_id(measurement.id) == compatible_id
    ]
    if len(matches) != 1:
        raise Measurement.DoesNotExist
    return matches[0]


class WeightEntryTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the weight entry overview resource
    """

    pk = '11111111-1111-1111-1111-000000000003'
    resource = Measurement
    private_resource = True
    date = timezone.now() - timezone.timedelta(days=25)
    data = {'weight': 100, 'date': date}

    def get_resource_name(self):
        return 'weightentry'

    def object_for_response_id(self, response_id):
        for entry in Measurement.objects.all():
            if compatible_weight_entry_id(entry.id) == response_id:
                return entry
        raise Measurement.DoesNotExist


class WeightEntryOfficialCategoryTestCase(api_base_test.ApiBaseTestCase, WgerTestCase):
    """
    Tests the automatic handling of the official body weight category
    """

    url = '/api/v2/weightentry/'

    def test_post_creates_official_category(self):
        """
        Test that POSTing without an official category creates one with the
        user's preferred weight unit
        """
        self.authenticate('admin')
        user = User.objects.get(username='admin')
        user.userprofile.weight_unit = 'lb'
        user.userprofile.save()

        response = self.client.post(self.url, data={'weight': 180, 'date': timezone.now()})
        self.assertEqual(response.status_code, 201)

        category = Category.objects.get(
            user=user,
            metric_type=MetricType.BODY_WEIGHT,
            is_official=True,
        )
        self.assertEqual(category.unit, 'lb')

    def test_post_reuses_official_category(self):
        """
        Test that POSTing with an existing official category does not create
        a second one
        """
        self.authenticate('test')
        count_before = Category.objects.filter(user__username='test').count()

        response = self.client.post(self.url, data={'weight': 82.5, 'date': timezone.now()})
        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            Category.objects.filter(user__username='test').count(),
            count_before,
        )


class WeightEntryUnitTestCase(api_base_test.ApiBaseTestCase, WgerTestCase):
    """
    Per-entry units on the legacy weight endpoint
    """

    url = '/api/v2/weightentry/'
    entry_pk = '11111111-1111-1111-1111-000000000001'  # 77, stored in kg

    def test_get_converts_to_profile_unit(self):
        """
        Test that entries in other units are converted to the profile unit
        """
        entry = Measurement.objects.get(pk=self.entry_pk)
        entry.extra_data = {'unit': 'lb'}
        entry.save()

        self.authenticate('test')
        response = self.client.get(f'{self.url}{self.entry_pk}/')

        self.assertEqual(response.status_code, 200)
        # 77 lb converted to the kg profile of user 'test'
        self.assertEqual(response.data['weight'], '34.93')

    def test_post_stamps_profile_unit(self):
        """
        Test that new entries are stamped with the user's weight unit
        """
        user = User.objects.get(username='test')
        user.userprofile.weight_unit = 'lb'
        user.userprofile.save()

        self.authenticate('test')
        response = self.client.post(self.url, {'weight': 180, 'date': timezone.now()})

        self.assertEqual(response.status_code, 201)
        entry = measurement_for_compatible_id(user, response.data['id'])
        self.assertEqual(entry.value, Decimal('180.00'))
        self.assertEqual(entry.extra_data, {'unit': 'lb'})

    def test_patch_weight_restamps_unit(self):
        """
        Test that updating the weight re-stamps the current profile unit
        """
        user = User.objects.get(username='test')
        user.userprofile.weight_unit = 'lb'
        user.userprofile.save()

        self.authenticate('test')
        response = self.client.patch(f'{self.url}{self.entry_pk}/', {'weight': 170})

        self.assertEqual(response.status_code, 200)
        entry = Measurement.objects.get(pk=self.entry_pk)
        self.assertEqual(entry.value, Decimal('170.00'))
        self.assertEqual(entry.extra_data, {'unit': 'lb'})

    def test_patch_weight_keeps_the_import_provenance(self):
        """
        Test that re-stamping the unit leaves the rest of extra_data alone
        """
        entry = Measurement.objects.get(pk=self.entry_pk)
        entry.extra_data = {
            'unit': 'kg',
            'source_unit': 'lb',
            'source_value': 169.76,
            'recording_method': 'automatic',
        }
        entry.save()

        self.authenticate('test')
        response = self.client.patch(f'{self.url}{self.entry_pk}/', {'weight': 78})

        self.assertEqual(response.status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(
            entry.extra_data,
            {
                'unit': 'kg',
                'source_unit': 'lb',
                'source_value': 169.76,
                'recording_method': 'automatic',
            },
        )

    def test_patch_date_keeps_unit(self):
        """
        Test that updates without a weight keep the stored unit
        """
        entry = Measurement.objects.get(pk=self.entry_pk)
        entry.extra_data = {'unit': 'lb'}
        entry.save()

        self.authenticate('test')
        response = self.client.patch(f'{self.url}{self.entry_pk}/', {'date': timezone.now()})

        self.assertEqual(response.status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.extra_data, {'unit': 'lb'})


class WeightEntryLimitsTestCase(api_base_test.ApiBaseTestCase, WgerTestCase):
    """
    The bounds of the legacy weight endpoint are the body weight bounds,
    resolved in the unit of the user profile
    """

    url = '/api/v2/weightentry/'

    def set_unit(self, unit):
        user = User.objects.get(username='test')
        user.userprofile.weight_unit = unit
        user.userprofile.save()

    def add_entry(self, weight):
        self.authenticate('test')
        return self.client.post(self.url, {'weight': weight, 'date': timezone.now()})

    def test_metric_bounds(self):
        """
        Test that a weight in kg is bounded by the kg limits
        """
        self.set_unit('kg')

        self.assertEqual(self.add_entry(340).status_code, 201)
        self.assertEqual(self.add_entry(360).status_code, 400)

    def test_imperial_bounds(self):
        """
        Test that the same weight in lb is bounded by the lb limits
        """
        self.set_unit('lb')

        self.assertEqual(self.add_entry(360).status_code, 201)
        self.assertEqual(self.add_entry(800).status_code, 400)


class WeightEntryTokenAuthTestCase(WgerTestCase):
    """
    The legacy token path openScale-sync uses

    It authenticates with `Authorization: Token`, never with JWT, and its
    update and delete first look an entry up by date. The 2.6 auth migration
    removed the login endpoints, so this is the contract the sync depends on.
    """

    url = '/api/v2/weightentry/'

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='test')
        self.token = create_token(self.user, force_new=True)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_crud_with_a_token(self):
        """
        Test that a token authenticates the whole find-then-modify cycle
        """
        date = timezone.now()

        response = self.client.post(
            self.url,
            {'weight': 81.5, 'date': date},
            content_type='application/json',
            **self.auth,
        )
        self.assertEqual(response.status_code, 201)
        pk = response.data['id']

        self.assertEqual(self.client.get(self.url, **self.auth).status_code, 200)

        response = self.client.patch(
            f'{self.url}{pk}/',
            {'weight': 82},
            content_type='application/json',
            **self.auth,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.delete(f'{self.url}{pk}/', **self.auth).status_code, 204)

    def test_without_a_token(self):
        """
        Test that the endpoint is not open to anonymous callers
        """
        self.assertEqual(self.client.get(self.url).status_code, 403)


class WeightEntryQueryCountTestCase(api_base_test.ApiBaseTestCase, WgerTestCase):
    """
    The endpoint returns the owner and the unit of every entry, both of which
    live on the category. openScale lists the whole history in one call
    """

    def add_entries(self, count: int, offset: int):
        category = Category.objects.get(
            user__username='test',
            metric_type=MetricType.BODY_WEIGHT,
            is_official=True,
        )
        Measurement.objects.bulk_create(
            Measurement(
                category=category,
                value=70,
                date=timezone.now() - timezone.timedelta(days=offset + i),
            )
            for i in range(count)
        )

    def test_listing_does_not_query_per_entry(self):
        """
        Test that the query count of a listing does not grow with the entries
        """
        self.authenticate('test')
        url = reverse('weightentry-list')

        # Warms the caches a first request fills (auth, user profile)
        self.client.get(url)

        self.add_entries(10, offset=100)
        with CaptureQueriesContext(connection) as short_list:
            self.assertEqual(self.client.get(url, {'limit': 100}).status_code, 200)

        self.add_entries(10, offset=200)
        with CaptureQueriesContext(connection) as long_list:
            self.assertEqual(self.client.get(url, {'limit': 100}).status_code, 200)

        self.assertEqual(len(long_list.captured_queries), len(short_list.captured_queries))


class WeightEntryCompatibleIdTestCase(api_base_test.ApiBaseTestCase, WgerTestCase):
    """
    openScale-sync stores weight entry ids as a Java long
    """

    url = '/api/v2/weightentry/'
    entry_pk = '11111111-1111-1111-1111-000000000001'

    def test_list_and_detail_use_a_signed_long(self):
        """
        Test that the public id fits in a signed 64-bit integer
        """
        entry = Measurement.objects.get(pk=self.entry_pk)
        expected = compatible_weight_entry_id(entry.id)

        self.authenticate('test')
        detail = self.client.get(f'{self.url}{self.entry_pk}/')
        self.assertEqual(detail.status_code, 200)
        self.assertIsInstance(detail.data['id'], int)
        self.assertEqual(detail.data['id'], expected)
        self.assertLessEqual(detail.data['id'], SIGNED_LONG_MAX)

        listing = self.client.get(self.url)
        ids = {row['id'] for row in listing.data['results']}
        self.assertIn(expected, ids)
        self.assertTrue(
            all(isinstance(row_id, int) and 0 <= row_id <= SIGNED_LONG_MAX for row_id in ids)
        )

    def test_numeric_id_round_trip(self):
        """
        Test that the number from the list can update and delete the entry
        """
        self.authenticate('test')
        compatible_id = compatible_weight_entry_id(uuid.UUID(self.entry_pk))

        response = self.client.patch(f'{self.url}{compatible_id}/', {'weight': 79})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], compatible_id)
        self.assertEqual(Measurement.objects.get(pk=self.entry_pk).value, Decimal('79.00'))

        self.assertEqual(self.client.delete(f'{self.url}{compatible_id}/').status_code, 204)
        self.assertFalse(Measurement.objects.filter(pk=self.entry_pk).exists())

    def test_unknown_numeric_id_is_not_found(self):
        """
        Test that a long which matches no entry is a 404
        """
        self.authenticate('test')
        self.assertEqual(self.client.get(f'{self.url}1/').status_code, 404)
