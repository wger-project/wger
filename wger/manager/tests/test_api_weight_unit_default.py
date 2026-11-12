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
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.consts import (
    WEIGHT_UNIT_KG,
    WEIGHT_UNIT_LB,
)
from wger.manager.models import (
    SlotEntry,
    WorkoutLog,
)


class SlotEntryWeightUnitDefaultTestCase(WgerTestCase):
    """
    Test that SlotEntry creation respects the user's profile weight_unit
    preference when no explicit weight_unit is provided.
    """

    def test_slot_entry_defaults_to_profile_kg(self):
        """
        When the user's profile weight_unit is 'kg' and no weight_unit is
        provided in the API request, the created SlotEntry should default
        to kg.
        """
        self.user_login('admin')

        # Ensure profile is set to kg
        profile = self.user.userprofile
        profile.weight_unit = 'kg'
        profile.save()

        response = self.client.post(
            reverse('slotentry-list'),
            data={
                'slot': 1,
                'exercise': 1,
                'type': 'normal',
                'order': 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        entry = SlotEntry.objects.get(pk=response.data['id'])
        self.assertEqual(entry.weight_unit_id, WEIGHT_UNIT_KG)

    def test_slot_entry_defaults_to_profile_lb(self):
        """
        When the user's profile weight_unit is 'lb' and no weight_unit is
        provided in the API request, the created SlotEntry should default
        to lb.
        """
        self.user_login('admin')

        # Set profile to lb
        profile = self.user.userprofile
        profile.weight_unit = 'lb'
        profile.save()

        response = self.client.post(
            reverse('slotentry-list'),
            data={
                'slot': 1,
                'exercise': 1,
                'type': 'normal',
                'order': 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        entry = SlotEntry.objects.get(pk=response.data['id'])
        self.assertEqual(entry.weight_unit_id, WEIGHT_UNIT_LB)

    def test_slot_entry_explicit_weight_unit_overrides_profile(self):
        """
        When an explicit weight_unit is provided in the API request, it
        should be used regardless of the user's profile preference.
        """
        self.user_login('admin')

        # Set profile to kg
        profile = self.user.userprofile
        profile.weight_unit = 'kg'
        profile.save()

        response = self.client.post(
            reverse('slotentry-list'),
            data={
                'slot': 1,
                'exercise': 1,
                'type': 'normal',
                'order': 1,
                'weight_unit': WEIGHT_UNIT_LB,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        entry = SlotEntry.objects.get(pk=response.data['id'])
        self.assertEqual(entry.weight_unit_id, WEIGHT_UNIT_LB)


class WorkoutLogWeightUnitDefaultTestCase(WgerTestCase):
    """
    Test that WorkoutLog creation respects the user's profile weight_unit
    preference when no explicit weight_unit is provided.
    """

    def test_workout_log_defaults_to_profile_lb(self):
        """
        When the user's profile weight_unit is 'lb' and no weight_unit is
        provided in the API request, the created WorkoutLog should default
        to lb.
        """
        self.user_login('admin')

        # Set profile to lb
        profile = self.user.userprofile
        profile.weight_unit = 'lb'
        profile.save()

        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'routine': 1,
                'slot_entry': 1,
                'exercise': 1,
                'repetitions': 10,
                'repetitions_unit': 1,
                'weight': 100,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        log = WorkoutLog.objects.get(pk=response.data['id'])
        self.assertEqual(log.weight_unit_id, WEIGHT_UNIT_LB)

    def test_workout_log_explicit_weight_unit_overrides_profile(self):
        """
        When an explicit weight_unit is provided in the API request, it
        should be used regardless of the user's profile preference.
        """
        self.user_login('admin')

        # Set profile to lb
        profile = self.user.userprofile
        profile.weight_unit = 'lb'
        profile.save()

        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'routine': 1,
                'slot_entry': 1,
                'exercise': 1,
                'repetitions': 10,
                'repetitions_unit': 1,
                'weight': 100,
                'weight_unit': WEIGHT_UNIT_KG,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        log = WorkoutLog.objects.get(pk=response.data['id'])
        self.assertEqual(log.weight_unit_id, WEIGHT_UNIT_KG)
