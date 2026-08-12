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
import logging

# Django
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import (
    Routine,
    SetsConfig,
    SlotEntry,
)


logger = logging.getLogger(__name__)


class CopyRoutineTestCase(WgerTestCase):
    """
    Tests copying a routine or template
    """

    def copy_routine_and_assert(self, pk: int):
        """
        Helper function to test copying routines
        """

        # Copy the routine
        count_before = Routine.objects.count()
        self.client.get(reverse('manager:routine:copy', kwargs={'pk': pk}))
        count_after = Routine.objects.count()

        self.assertEqual(count_after, count_before + 1)

        routine_original = Routine.objects.get(pk=pk)
        routine_copy = Routine.objects.latest('pk')

        self.assertEqual(routine_copy.name, routine_original.name)
        self.assertEqual(routine_copy.description, routine_original.description)

        # Copies are always private, regular routines
        self.assertFalse(routine_copy.is_template)
        self.assertFalse(routine_copy.is_public)
        self.assertEqual(routine_copy.start, datetime.date.today())
        self.assertEqual(routine_copy.end, datetime.date.today() + routine_original.duration)

        days_original = routine_original.days.all()
        days_copy = routine_copy.days.all()

        # Test that the different attributes and objects are correctly copied over
        for i in range(0, routine_original.days.count()):
            self.assertEqual(days_original[i].order, days_copy[i].order)
            self.assertEqual(days_original[i].name, days_copy[i].name)
            self.assertEqual(days_original[i].description, days_copy[i].description)
            self.assertEqual(days_original[i].type, days_copy[i].type)
            self.assertEqual(days_original[i].is_rest, days_copy[i].is_rest)
            self.assertEqual(
                days_original[i].need_logs_to_advance, days_copy[i].need_logs_to_advance
            )

            slots_original = days_original[i].slots.all()
            slots_copy = days_copy[i].slots.all()

            for j in range(days_original[i].slots.count()):
                self.assertEqual(slots_original[j].order, slots_copy[j].order)
                self.assertEqual(slots_original[j].comment, slots_copy[j].comment)

                slot_entries_original = slots_original[j].entries.all()
                slot_entries_copy = slots_copy[j].entries.all()

                for k in range(slot_entries_original.count()):
                    entry_copy = slot_entries_copy[k]
                    entry_orig = slot_entries_original[k]

                    self.assertEqual(entry_orig.exercise_id, entry_copy.exercise_id)
                    self.assertEqual(entry_orig.repetition_unit_id, entry_copy.repetition_unit_id)
                    self.assertEqual(entry_orig.repetition_rounding, entry_copy.repetition_rounding)
                    self.assertEqual(entry_orig.weight_unit_id, entry_copy.weight_unit_id)
                    self.assertEqual(entry_orig.weight_rounding, entry_copy.weight_rounding)
                    self.assertEqual(entry_orig.type, entry_copy.type)

                    # TODO: check the rest of the config objects
                    configs_orig = entry_orig.setsconfig_set.all()
                    configs_copy = entry_copy.setsconfig_set.all()
                    for m in range(entry_orig.setsconfig_set.count()):
                        self.assertEqual(configs_orig[m].value, configs_copy[m].value)

    def test_copy_workout_owner(self):
        """
        Test copying a full workout with days, slots, entries and configs
        """

        # Guard against empty fixtures, the deep comparison would silently
        # collapse into zero iterations
        self.assertTrue(Routine.objects.get(pk=1).days.count())
        self.assertTrue(SlotEntry.objects.filter(slot__day__routine_id=1).exists())
        self.assertTrue(SetsConfig.objects.filter(slot_entry__slot__day__routine_id=1).exists())

        self.user_login('admin')
        self.copy_routine_and_assert(pk=1)

    def test_copy_empty_routine(self):
        """
        Test copying a routine without any days
        """
        self.assertFalse(Routine.objects.get(pk=3).days.count())

        self.user_login('test')
        self.copy_routine_and_assert(pk=3)

    def test_copy_workout_other(self):
        """
        Test copying a workout (not template) from another user
        """
        self.user_login('admin')
        response = self.client.get(reverse('manager:routine:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 403)

    def test_copy_template_no_public_other_user(self):
        """
        Test copying a workout template that is not marked as public and belongs to another user
        """
        routine = Routine.objects.get(pk=3)
        routine.is_template = True
        routine.save()

        self.user_login('admin')
        response = self.client.get(reverse('manager:routine:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 403)

    def test_copy_template_no_public_owner_user(self):
        """
        Test copying a workout template that is not marked as public and belongs to the current user
        """
        routine = Routine.objects.get(pk=3)
        routine.is_template = True
        routine.save()

        self.user_login('test')
        response = self.client.get(reverse('manager:routine:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 302)

    def test_copy_template_public_other_user(self):
        """
        Test copying a workout template that is marked as public and belongs to another user
        """
        routine = Routine.objects.get(pk=3)
        routine.is_template = True
        routine.is_public = True
        routine.save()

        self.user_login('admin')
        response = self.client.get(reverse('manager:routine:copy', kwargs={'pk': '3'}))
        self.assertEqual(response.status_code, 302)
