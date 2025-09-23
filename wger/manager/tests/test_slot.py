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


# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import (
    SetsConfig,
    Slot,
    SlotEntry,
)


class SlotTestCase(WgerTestCase):
    """
    Test the slot calculations
    """

    slot: Slot

    def setUp(self):
        super().setUp()

        self.slot = Slot(day_id=1, order=1)
        self.slot.save()

        entry1 = SlotEntry(id=100, slot=self.slot, exercise_id=1, order=1)
        entry1.save()
        SetsConfig(slot_entry=entry1, iteration=1, value=4).save()

        entry2 = SlotEntry(id=101, slot=self.slot, exercise_id=2, order=2)
        entry2.save()
        SetsConfig(slot_entry=entry2, iteration=1, value=3).save()

        entry3 = SlotEntry(id=102, slot=self.slot, exercise_id=3, order=3)
        entry3.save()
        SetsConfig(slot_entry=entry3, iteration=1, value=2).save()

    def test_get_sets(self):
        """
        Test that the correct sets are returned for supersets
        """

        result = self.slot.set_data_gym(1)

        self.assertEqual(len(result), 9)

        self.assertEqual(result[0].exercise, 1)
        self.assertEqual(result[0].sets, 1)
        self.assertEqual(result[1].exercise, 2)
        self.assertEqual(result[1].sets, 1)
        self.assertEqual(result[2].exercise, 3)
        self.assertEqual(result[2].sets, 1)

        self.assertEqual(result[3].exercise, 1)
        self.assertEqual(result[4].exercise, 2)
        self.assertEqual(result[5].exercise, 3)

        self.assertEqual(result[6].exercise, 1)
        self.assertEqual(result[7].exercise, 2)
        self.assertEqual(result[8].exercise, 1)

    def test_get_sets_one_exercise(self):
        """
        Test that the correct sets are returned for regular sets
        """
        SlotEntry.objects.filter(id__in=(101, 102)).delete()

        result = self.slot.set_data_gym(1)

        self.assertEqual(len(result), 4)
        for i in range(0, 3):
            self.assertEqual(result[i].exercise, 1)
            self.assertEqual(result[i].sets, 1)
