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
from decimal import Decimal

# Django
from django.contrib.auth.models import User
from django.utils import timezone

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType
from wger.weight.models import WeightEntry


class MealRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(
            str(WeightEntry.objects.get(pk=1)), '2012-10-01 14:30:21.592000+00:00: 77.00 kg'
        )


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
        entry = Measurement.objects.get(pk=response.data['id'])
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
