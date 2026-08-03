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

# Third Party
from rest_framework import status

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
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

    pk = 3
    resource = WeightEntry
    private_resource = True
    date = timezone.now() - timezone.timedelta(days=25)
    data = {'weight': 100, 'date': date}

    def test_post_imperial_weight_is_converted_to_kg(self):
        """
        Test that users using lb can submit body weight in lb.
        """
        self.authenticate('trainer4')

        response = self.client.post(
            self.url,
            data={'weight': 365, 'date': self.date},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        entry = WeightEntry.objects.get(pk=response.data['id'])
        self.assertEqual(entry.user, User.objects.get(username='trainer4'))
        self.assertEqual(entry.weight, Decimal('165.56'))

    def test_post_imperial_weight_above_kg_limit_fails(self):
        """
        Test that lb input is still validated against the kg storage limit.
        """
        self.authenticate('trainer4')

        response = self.client.post(
            self.url,
            data={'weight': 1323, 'date': self.date},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('weight', response.data)
