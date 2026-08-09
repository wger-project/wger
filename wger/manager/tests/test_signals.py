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
    Day,
    Routine,
    Slot,
    SlotEntry,
    WeightConfig,
    WorkoutLog,
    WorkoutSession,
)


class StaleRelationSignalsTestCase(WgerTestCase):
    """
    Test that deleting objects whose related rows are already gone does not error

    The stale instances mirror what the deletion collector of a second, concurrent
    request holds after the first request's cascade delete has been committed.
    """

    def test_delete_day_with_deleted_routine(self):
        """A day whose routine is already deleted can be deleted without error"""

        day = Slot.objects.get(pk=1).day
        stale_day = Day.objects.get(pk=day.pk)

        day.routine.delete()

        stale_day.delete()

    def test_delete_slot_with_deleted_day(self):
        """A slot whose day is already deleted can be deleted without error"""

        slot = Slot.objects.get(pk=1)
        stale_slot = Slot.objects.get(pk=1)

        slot.day.delete()

        stale_slot.delete()

    def test_delete_slot_entry_with_deleted_slot(self):
        """A slot entry whose slot is already deleted can be deleted without error"""

        entry = SlotEntry(slot_id=1, exercise_id=1)
        entry.save()
        stale_entry = SlotEntry.objects.get(pk=entry.pk)

        Slot.objects.get(pk=1).delete()

        stale_entry.delete()

    def test_delete_config_with_deleted_slot_entry(self):
        """A config whose slot entry is already deleted can be deleted without error"""

        entry = SlotEntry(slot_id=1, exercise_id=1)
        entry.save()
        WeightConfig(slot_entry=entry, iteration=1, value=80).save()
        stale_config = WeightConfig.objects.get(slot_entry_id=entry.pk)

        entry.delete()

        stale_config.delete()

    def test_delete_workout_log_with_deleted_routine(self):
        """A workout log whose routine is already deleted can be deleted without error"""

        log = WorkoutLog(user_id=1, exercise_id=1, routine_id=1, weight=80, repetitions=5)
        log.save()
        stale_log = WorkoutLog.objects.get(pk=log.pk)

        Routine.objects.get(pk=1).delete()

        stale_log.delete()

    def test_delete_workout_session_with_deleted_routine(self):
        """A workout session whose routine is already deleted can be deleted without error"""

        session = WorkoutSession(user_id=1, routine_id=1)
        session.save()
        stale_session = WorkoutSession.objects.get(pk=session.pk)

        Routine.objects.get(pk=1).delete()

        stale_session.delete()
