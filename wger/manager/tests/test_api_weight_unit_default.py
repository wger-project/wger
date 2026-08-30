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
from wger.manager.models import (
    SlotEntry,
    WorkoutLog,
)


class SlotEntryWeightUnitDefaultTestCase(WgerTestCase):
    """
    New slot entries pre-select the routine owner's profile weight unit.

    Fixture: slot pk=1 belongs to admin's routine. Admin's profile defaults to kg.
    """

    def setUp(self):
        super().setUp()
        self.user_login('admin')
        self.profile = User.objects.get(username='admin').userprofile

    def _set_profile_unit(self, unit: str):
        self.profile.weight_unit = unit
        self.profile.save()

    def _create_entry(self, **extra):
        payload = {
            'slot': 1,
            'exercise': 1,
        }
        payload.update(extra)
        return self.client.post(
            reverse('slot-entry-list'),
            data=payload,
            content_type='application/json',
        )

    def test_new_entry_uses_profile_kg(self):
        self._set_profile_unit('kg')

        response = self._create_entry()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        entry = SlotEntry.objects.get(pk=response.data['id'])
        self.assertEqual(entry.weight_unit_id, WEIGHT_UNIT_KG)

    def test_new_entry_uses_profile_lb(self):
        self._set_profile_unit('lb')

        response = self._create_entry()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        entry = SlotEntry.objects.get(pk=response.data['id'])
        self.assertEqual(entry.weight_unit_id, WEIGHT_UNIT_LB)

    def test_explicit_unit_overrides_profile(self):
        self._set_profile_unit('lb')

        response = self._create_entry(weight_unit=WEIGHT_UNIT_KG)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        entry = SlotEntry.objects.get(pk=response.data['id'])
        self.assertEqual(entry.weight_unit_id, WEIGHT_UNIT_KG)

    def test_edit_preserves_stored_unit_after_profile_change(self):
        self._set_profile_unit('kg')
        create = self._create_entry()
        self.assertEqual(create.status_code, status.HTTP_201_CREATED, create.content)
        entry_id = create.data['id']
        self.assertEqual(SlotEntry.objects.get(pk=entry_id).weight_unit_id, WEIGHT_UNIT_KG)

        self._set_profile_unit('lb')
        response = self.client.patch(
            reverse('slot-entry-detail', kwargs={'pk': entry_id}),
            data={'comment': 'keep unit'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(SlotEntry.objects.get(pk=entry_id).weight_unit_id, WEIGHT_UNIT_KG)

    def test_profile_change_only_affects_new_entries(self):
        self._set_profile_unit('lb')
        first = self._create_entry()
        self.assertEqual(first.status_code, status.HTTP_201_CREATED, first.content)
        first_id = first.data['id']
        self.assertEqual(SlotEntry.objects.get(pk=first_id).weight_unit_id, WEIGHT_UNIT_LB)

        self._set_profile_unit('kg')
        second = self._create_entry()
        self.assertEqual(second.status_code, status.HTTP_201_CREATED, second.content)

        self.assertEqual(SlotEntry.objects.get(pk=first_id).weight_unit_id, WEIGHT_UNIT_LB)
        self.assertEqual(SlotEntry.objects.get(pk=second.data['id']).weight_unit_id, WEIGHT_UNIT_KG)


class WorkoutLogWeightUnitDefaultTestCase(WgerTestCase):
    """
    New workout logs pre-select the user's profile weight unit.

    Fixture: slot_entry pk=1 and routine pk=1 belong to admin.
    """

    def setUp(self):
        super().setUp()
        self.user_login('admin')
        self.profile = User.objects.get(username='admin').userprofile

    def _set_profile_unit(self, unit: str):
        self.profile.weight_unit = unit
        self.profile.save()

    def _create_log(self, **extra):
        payload = {
            'routine': 1,
            'slot_entry': 1,
            'exercise': 1,
            'repetitions': 10,
            'repetitions_unit': 1,
            'weight': 100,
            'date': '2024-01-01',
        }
        payload.update(extra)
        return self.client.post(
            reverse('workoutlog-list'),
            data=payload,
            content_type='application/json',
        )

    def test_new_log_uses_profile_lb(self):
        self._set_profile_unit('lb')

        response = self._create_log()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        log = WorkoutLog.objects.get(pk=response.data['id'])
        self.assertEqual(log.weight_unit_id, WEIGHT_UNIT_LB)

    def test_explicit_unit_overrides_profile(self):
        self._set_profile_unit('lb')

        response = self._create_log(weight_unit=WEIGHT_UNIT_KG)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        log = WorkoutLog.objects.get(pk=response.data['id'])
        self.assertEqual(log.weight_unit_id, WEIGHT_UNIT_KG)

    def test_edit_preserves_stored_unit_after_profile_change(self):
        self._set_profile_unit('kg')
        create = self._create_log()
        self.assertEqual(create.status_code, status.HTTP_201_CREATED, create.content)
        log_id = create.data['id']
        self.assertEqual(WorkoutLog.objects.get(pk=log_id).weight_unit_id, WEIGHT_UNIT_KG)

        self._set_profile_unit('lb')
        response = self.client.patch(
            reverse('workoutlog-detail', kwargs={'pk': log_id}),
            data={'weight': 101},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(WorkoutLog.objects.get(pk=log_id).weight_unit_id, WEIGHT_UNIT_KG)
