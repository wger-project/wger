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
from wger.manager.dataclasses import SetConfigData
from wger.manager.models import Day


class DaySlotTestCase(WgerTestCase):
    """
    Test that the correct slots are calculated
    """

    def test_slots_gym_mode(self):
        """
        Test that the correct slots are returned - gym mode
        """

        day = Day.objects.get(pk=1)
        slots = day.get_slots_gym_mode(1)
        set_configs = slots[0].sets

        config_1 = SetConfigData(
            slot_config_id=1,
            exercise=1,
            weight=80,
            reps=4,
            rir=None,
            rest=None,
            sets=1,
        )
        config_2 = SetConfigData(
            slot_config_id=2,
            exercise=2,
            weight=20,
            reps=5,
            rir=None,
            rest=None,
            sets=1,
        )

        # Sets are returned interleaved from the supersets
        self.assertEqual(len(set_configs), 7)
        self.assertEqual(set_configs[0], config_1)
        self.assertEqual(set_configs[1], config_2)
        self.assertEqual(set_configs[2], config_1)
        self.assertEqual(set_configs[3], config_2)
        self.assertEqual(set_configs[4], config_1)
        self.assertEqual(set_configs[5], config_1)
        self.assertEqual(set_configs[6], config_1)

    def test_slots_display_mode(self):
        """
        Test that the correct slots are returned - display mode
        """

        day = Day.objects.get(pk=1)
        slots = day.get_slots_display_mode(1)

        slot1 = slots[0]
        set_configs_1 = slot1.sets

        slot2 = slots[1]
        set_configs_2 = slot2.sets

        # Exercises in superset are returned individually, not interleaved
        self.assertEqual(slot1.comment, 'test comment 123')
        self.assertEqual(slot1.exercises, [1, 2])
        self.assertEqual(len(set_configs_1), 2)
        self.assertEqual(
            set_configs_1[0],
            SetConfigData(
                slot_config_id=1,
                exercise=1,
                weight=80,
                reps=4,
                rir=None,
                rest=None,
                sets=5,
            ),
        )
        self.assertEqual(
            set_configs_1[1],
            SetConfigData(
                slot_config_id=2,
                exercise=2,
                weight=20,
                reps=5,
                rir=None,
                rest=None,
                sets=2,
            ),
        )

        # If there are consecutive slots with the same exercise, group them
        self.assertEqual(slot2.comment, 'test comment 456')
        self.assertEqual(slot2.exercises, [3])
        self.assertEqual(len(set_configs_2), 2)
        self.assertEqual(
            set_configs_2[0],
            SetConfigData(
                slot_config_id=3,
                exercise=3,
                weight=80,
                reps=6,
                rir=None,
                rest=None,
                sets=5,
            ),
        )

        self.assertEqual(
            set_configs_2[1],
            SetConfigData(
                slot_config_id=4,
                exercise=3,
                weight=50,
                reps=4,
                rir=None,
                rest=None,
                sets=3,
            ),
        )
