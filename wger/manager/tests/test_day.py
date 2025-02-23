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
from dataclasses import asdict
from decimal import Decimal

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.dataclasses import SetConfigData
from wger.manager.models import (
    Day,
    WorkoutLog,
)


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
            slot_entry_id=1,
            exercise=1,
            weight=80,
            weight_rounding=Decimal('1.25'),
            weight_unit=1,
            weight_unit_name='kg',
            repetitions=4,
            repetitions_rounding=Decimal('1.00'),
            repetitions_unit=1,
            repetitions_unit_name='Repetitions',
            rir=None,
            rest=None,
            sets=1,
        )
        config_2 = SetConfigData(
            slot_entry_id=2,
            exercise=2,
            weight=20,
            weight_rounding=Decimal('1.25'),
            weight_unit=1,
            weight_unit_name='kg',
            repetitions=5,
            repetitions_rounding=Decimal('1.00'),
            repetitions_unit=1,
            repetitions_unit_name='Repetitions',
            rir=None,
            rest=None,
            sets=1,
        )

        # Sets are returned interleaved from the supersets
        self.assertEqual(len(set_configs), 7)
        self.assertDictEqual(asdict(set_configs[0]), asdict(config_1))
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
        self.assertDictEqual(
            asdict(set_configs_1[0]),
            asdict(
                SetConfigData(
                    slot_entry_id=1,
                    exercise=1,
                    weight=80,
                    weight_rounding=Decimal('1.25'),
                    weight_unit=1,
                    weight_unit_name='kg',
                    repetitions=Decimal(4),
                    repetitions_rounding=Decimal('1.00'),
                    repetitions_unit=1,
                    repetitions_unit_name='Repetitions',
                    rir=None,
                    rest=None,
                    sets=5,
                )
            ),
        )
        self.assertDictEqual(
            asdict(set_configs_1[1]),
            asdict(
                SetConfigData(
                    slot_entry_id=2,
                    exercise=2,
                    weight=20,
                    weight_rounding=Decimal('1.25'),
                    weight_unit=1,
                    weight_unit_name='kg',
                    repetitions=5,
                    repetitions_rounding=Decimal('1.00'),
                    repetitions_unit=1,
                    repetitions_unit_name='Repetitions',
                    rir=None,
                    rest=None,
                    sets=2,
                )
            ),
        )

        # If there are consecutive slots with the same exercise, group them
        self.assertEqual(slot2.comment, 'test comment 456')
        self.assertEqual(slot2.exercises, [3])
        self.assertEqual(len(set_configs_2), 2)
        self.assertDictEqual(
            asdict(set_configs_2[0]),
            asdict(
                SetConfigData(
                    slot_entry_id=3,
                    exercise=3,
                    weight=80,
                    weight_rounding=Decimal('1.25'),
                    weight_unit=1,
                    weight_unit_name='kg',
                    repetitions=6,
                    repetitions_rounding=Decimal('1.00'),
                    repetitions_unit=1,
                    repetitions_unit_name='Repetitions',
                    rir=None,
                    rest=None,
                    sets=5,
                )
            ),
        )

        self.assertDictEqual(
            asdict(set_configs_2[1]),
            asdict(
                SetConfigData(
                    slot_entry_id=4,
                    exercise=3,
                    weight=50,
                    weight_rounding=Decimal('1.25'),
                    weight_unit=1,
                    weight_unit_name='kg',
                    repetitions=4,
                    repetitions_rounding=Decimal('1.00'),
                    repetitions_unit=1,
                    repetitions_unit_name='Repetitions',
                    rir=None,
                    rest=None,
                    sets=3,
                )
            ),
        )


class DayModelTestCase(WgerTestCase):
    """
    Tests the day model
    """

    def test_rest_day(self):
        """
        Test that a day marked as a rest day deletes all slots
        """

        day = Day.objects.get(pk=1)
        self.assertEqual(day.slots.count(), 3)

        day.is_rest = True
        day.save()
        self.assertEqual(day.slots.count(), 0)

    def test_no_rest_day(self):
        """
        Test that a regular day does not delete any slots
        """

        day = Day.objects.get(pk=1)
        self.assertEqual(day.slots.count(), 3)

        day.name = 'foo'
        day.save()
        self.assertEqual(day.slots.count(), 3)

    def test_can_proceed_future(self):
        """
        Test that can_proceed returns true when the date is in the future
        """

        day = Day.objects.get(pk=1)
        self.assertTrue(day.can_proceed(date=datetime.date.today() + datetime.timedelta(days=1)))

    def test_can_proceed_present(self):
        """
        Test that can_proceed returns true when need_logs_to_advance is false
        """

        day = Day.objects.get(pk=1)
        day.need_logs_to_advance = False
        self.assertTrue(day.can_proceed(date=datetime.date.today()))

    def test_can_proceed_no_logs(self):
        """
        Test that can_proceed returns false when need_logs_to_advance is true and there are no logs
        """

        day = Day.objects.get(pk=1)
        day.need_logs_to_advance = True
        self.assertFalse(day.can_proceed(date=datetime.date.today()))

    def test_can_proceed(self):
        """
        Test that can_proceed returns true when need_logs_to_advance is true and there are logs
        """

        day = Day.objects.get(pk=1)
        day.need_logs_to_advance = True
        WorkoutLog.objects.create(
            date=datetime.datetime.now(),
            weight_unit_id=1,
            repetitions_unit_id=1,
            user=day.routine.user,
            repetitions=1,
            weight=1,
            exercise_id=1,
        )
        self.assertFalse(day.can_proceed(date=datetime.date.today()))
