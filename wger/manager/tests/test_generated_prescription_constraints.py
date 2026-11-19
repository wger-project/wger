# This file is part of wger Workout Manager.
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import datetime
from decimal import Decimal

# Django
from django.test import SimpleTestCase

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.api.serializers import SetConfigDataSerializer
from wger.manager.dataclasses import SetConfigData
from wger.manager.models import (
    Day,
    MaxRiRConfig,
    RiRConfig,
    Routine,
    Slot,
    SlotEntry,
)


class GeneratedPrescriptionTextConstraintsTestCase(SimpleTestCase):
    def test_text_preserves_set_range_starting_at_one(self):
        prescription = SetConfigData(
            exercise=1,
            sets=1,
            max_sets=3,
            repetitions=8,
            repetitions_unit=1,
        )

        self.assertEqual(prescription.text_repr, '1-3 Sets, 8 Reps')

    def test_text_preserves_explicit_zero_rir(self):
        prescription = SetConfigData(
            exercise=1,
            repetitions=8,
            repetitions_unit=1,
            rir=Decimal('0'),
        )

        self.assertEqual(prescription.text_repr, '8 Reps @ 0 RiR')


class GeneratedRoutineConstraintsTestCase(WgerTestCase):
    def test_weekly_cycle_wrapping_on_monday_does_not_skip_a_week(self):
        routine = Routine.objects.create(
            user_id=1,
            name='Friday start',
            start=datetime.date(2026, 10, 30),
            end=datetime.date(2026, 11, 8),
            fit_in_week=True,
        )
        days = [Day.objects.create(routine=routine, order=i, name=f'Day {i}') for i in range(1, 4)]

        self.assertEqual(routine.data_for_day(datetime.date(2026, 11, 1)).day, days[2])
        self.assertEqual(routine.data_for_day(datetime.date(2026, 11, 2)).day, days[0])

    def test_generated_json_preserves_rir_range_starting_at_zero(self):
        slot = Slot.objects.create(day_id=1, order=100)
        entry = SlotEntry.objects.create(slot=slot, exercise_id=1)
        RiRConfig.objects.create(slot_entry=entry, iteration=1, value=0)
        MaxRiRConfig.objects.create(slot_entry=entry, iteration=1, value=2)

        data = SetConfigDataSerializer(entry.get_config_data(1)).data

        self.assertEqual(Decimal(data['rir']), Decimal('0'))
        self.assertIsNotNone(data['max_rir'], 'The stored upper RiR target was lost')
        self.assertEqual(Decimal(data['max_rir']), Decimal('2'))
