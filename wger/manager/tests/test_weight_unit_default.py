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

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.consts import (
    WEIGHT_UNIT_KG,
    WEIGHT_UNIT_LB,
)


class WeightUnitDefaultTestCase(WgerTestCase):
    """
    New slot entries and logs take the weight unit from the user's profile
    when the client does not send one (wger-project/wger#2205)
    """

    def setUp(self):
        super().setUp()
        self.user_login('admin')

        profile = User.objects.get(username='admin').userprofile
        profile.weight_unit = 'lb'
        profile.save()

    def create_slot_entry(self, **extra):
        return self.client.post(
            reverse('slot-entry-list'),
            data={'slot': 1, 'exercise': 1, 'order': 1, **extra},
            content_type='application/json',
        )

    def test_slot_entry_uses_profile_unit(self):
        response = self.create_slot_entry()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertEqual(response.json()['weight_unit'], WEIGHT_UNIT_LB)

    def test_slot_entry_keeps_explicit_unit(self):
        response = self.create_slot_entry(weight_unit=WEIGHT_UNIT_KG)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertEqual(response.json()['weight_unit'], WEIGHT_UNIT_KG)

    def test_log_uses_profile_unit(self):
        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'exercise': 1,
                'routine': 1,
                'date': datetime.date(2025, 10, 1).isoformat(),
                'weight': 30,
                'repetitions': 8,
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertEqual(response.json()['weight_unit'], WEIGHT_UNIT_LB)
