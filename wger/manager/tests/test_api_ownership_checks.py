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
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import (
    Day,
    SlotEntry,
    WorkoutLog,
    WorkoutSession,
)


class WorkoutLogSlotEntryOwnershipTestCase(WgerTestCase):
    """
    Make sure the API rejects cross-user references on the ``slot_entry``
    foreign key when creating or updating a WorkoutLog.

    Slot entry pk=1 belongs to routine pk=1 (user 'admin', pk=1).
    Routine pk=2 belongs to user 'test' (pk=2).
    """

    def test_create_with_foreign_slot_entry_is_forbidden(self):
        """
        POST /api/v2/workoutlog/ from user 'test' must not be able to attach
        a log to admin's slot_entry, even if the request's ``routine`` is
        owned by user 'test'.
        """
        self.user_login('test')

        victim_slot_entry = SlotEntry.objects.get(pk=1)
        self.assertEqual(victim_slot_entry.slot.day.routine.user_id, 1)

        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'routine': 2,
                'slot_entry': victim_slot_entry.pk,
                'exercise': 1,
                'repetitions': 999,
                'repetitions_unit': 1,
                'weight': 999,
                'weight_unit': 1,
                'date': '2024-01-01',
                'iteration': 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            WorkoutLog.objects.filter(slot_entry=victim_slot_entry, weight=999).exists()
        )

    def test_create_with_own_slot_entry_is_allowed(self):
        """
        Ensure the new ownership check does not break the legitimate case.
        """
        self.user_login()

        own_slot_entry = SlotEntry.objects.get(pk=1)
        self.assertEqual(own_slot_entry.slot.day.routine.user_id, 1)

        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'routine': 1,
                'slot_entry': own_slot_entry.pk,
                'exercise': 1,
                'repetitions': 5,
                'repetitions_unit': 1,
                'weight': 50,
                'weight_unit': 1,
                'date': '2024-01-01',
                'iteration': 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class WorkoutLogNextLogOwnershipTestCase(WgerTestCase):
    """
    Make sure the API rejects cross-user references on the ``next_log``
    foreign key. Without the ownership check the model save() silently
    nulls the field, but the API should respond with 403 for consistency
    with the other foreign keys on this resource.

    WorkoutLog pk=1 belongs to user 'admin' (pk=1).
    Routine pk=3 belongs to user 'test' (pk=2).
    """

    def test_create_with_foreign_next_log_is_forbidden(self):
        self.user_login('test')

        victim_log = WorkoutLog.objects.get(pk=1)
        self.assertEqual(victim_log.user_id, 1)

        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'routine': 3,
                'next_log': victim_log.pk,
                'exercise': 1,
                'repetitions': 5,
                'repetitions_unit': 1,
                'weight': 50,
                'weight_unit': 1,
                'date': '2024-01-01',
                'iteration': 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WorkoutSessionDayOwnershipTestCase(WgerTestCase):
    """
    Make sure the API rejects cross-user references on the ``day``
    foreign key when creating a WorkoutSession.

    Day pk=1 belongs to routine pk=1 (user 'admin', pk=1).
    Routine pk=3 belongs to user 'test' (pk=2).
    """

    def test_create_with_foreign_day_is_forbidden(self):
        self.user_login('test')

        victim_day = Day.objects.get(pk=1)
        self.assertEqual(victim_day.routine.user_id, 1)

        response = self.client.post(
            reverse('workoutsession-list'),
            data={
                'routine': 3,
                'day': victim_day.pk,
                'date': '2024-02-01',
                'notes': '',
                'impression': '2',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(WorkoutSession.objects.filter(day=victim_day, routine_id=3).exists())

    def test_create_with_own_day_is_allowed(self):
        """
        Smoke test: the legitimate case (own routine + own day) still works.
        Day pk=1 belongs to user 'admin'.
        """
        self.user_login()

        own_day = Day.objects.get(pk=1)
        self.assertEqual(own_day.routine.user_id, 1)

        response = self.client.post(
            reverse('workoutsession-list'),
            data={
                'routine': 1,
                'day': own_day.pk,
                'date': '2024-02-15',
                'notes': '',
                'impression': '2',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
