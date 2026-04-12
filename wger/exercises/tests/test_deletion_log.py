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
from uuid import UUID

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    DeletionLog,
    Exercise,
    Translation,
)
from wger.manager.models import WorkoutLog
from wger.manager.models.slot_entry import SlotEntry


class DeletionLogTestCase(WgerTestCase):
    """
    Test that the deletion log entries are correctly generated
    """

    def test_exercise(self):
        """
        Test that an entry is generated when a base is deleted
        """
        self.assertEqual(DeletionLog.objects.all().count(), 0)

        exercise = Exercise.objects.get(pk=1)
        exercise.delete()

        # Exercise is deleted
        count_exercise_logs = DeletionLog.objects.filter(
            model_type=DeletionLog.MODEL_EXERCISE,
            uuid=exercise.uuid,
        ).count()
        log = DeletionLog.objects.get(pk=1)

        self.assertEqual(count_exercise_logs, 1)
        self.assertEqual(log.model_type, DeletionLog.MODEL_EXERCISE)
        self.assertEqual(log.uuid, exercise.uuid)
        self.assertEqual(log.comment, 'Exercise base of An exercise')
        self.assertEqual(log.replaced_by, None)

        # All translations are also deleted
        count = DeletionLog.objects.filter(model_type=DeletionLog.MODEL_TRANSLATION).count()
        self.assertEqual(count, 2)

        # First translation
        log2 = DeletionLog.objects.get(pk=4)
        self.assertEqual(log2.model_type, DeletionLog.MODEL_TRANSLATION)
        self.assertEqual(log2.uuid, UUID('9838235c-e38f-4ca6-921e-9d237d8e0813'))
        self.assertEqual(log2.comment, 'An exercise')
        self.assertEqual(log2.replaced_by, None)

        # Second translation
        log3 = DeletionLog.objects.get(pk=5)
        self.assertEqual(log3.model_type, DeletionLog.MODEL_TRANSLATION)
        self.assertEqual(log3.uuid, UUID('13b532f9-d208-462e-a000-7b9982b2b53e'))
        self.assertEqual(log3.comment, 'Test exercise 123')
        self.assertEqual(log3.replaced_by, None)

    def test_exercise_with_replaced_by(self):
        """
        Test that an entry is generated when a exercise is deleted and the replaced by is
        set correctly
        """
        self.assertEqual(DeletionLog.objects.all().count(), 0)

        exercise = Exercise.objects.get(pk=1)
        exercise.delete(replace_by='ae3328ba-9a35-4731-bc23-5da50720c5aa')

        # Exercise is deleted
        log = DeletionLog.objects.get(pk=1)

        self.assertEqual(log.model_type, DeletionLog.MODEL_EXERCISE)
        self.assertEqual(log.uuid, exercise.uuid)
        self.assertEqual(log.replaced_by, UUID('ae3328ba-9a35-4731-bc23-5da50720c5aa'))

    def test_exercise_replace_by_updates_workout_logs(self):
        """
        Test that workout logs referencing the deleted exercise are updated
        to point to the replacement exercise
        """
        exercise_to_delete = Exercise.objects.get(pk=1)
        replacement = Exercise.objects.get(pk=2)

        # Exercise 1 has 4 workout logs, exercise 2 has 1
        self.assertEqual(WorkoutLog.objects.filter(exercise=exercise_to_delete).count(), 4)
        self.assertEqual(WorkoutLog.objects.filter(exercise=replacement).count(), 1)

        exercise_to_delete.delete(replace_by=str(replacement.uuid))

        # All workout logs should now point to the replacement
        self.assertEqual(WorkoutLog.objects.filter(exercise=replacement).count(), 5)

    def test_exercise_replace_by_updates_slot_entries(self):
        """
        Test that routine slot entries referencing the deleted exercise are
        updated to point to the replacement exercise
        """
        exercise_to_delete = Exercise.objects.get(pk=1)
        replacement = Exercise.objects.get(pk=2)

        # Exercise 1 has 1 slot entry, exercise 2 has 1
        self.assertEqual(SlotEntry.objects.filter(exercise=exercise_to_delete).count(), 1)
        self.assertEqual(SlotEntry.objects.filter(exercise=replacement).count(), 1)

        exercise_to_delete.delete(replace_by=str(replacement.uuid))

        # The slot entry should now point to the replacement
        self.assertEqual(SlotEntry.objects.filter(exercise=replacement).count(), 2)

    def test_exercise_delete_without_replace_by_does_not_keep_references(self):
        """
        Test that deleting without replace_by does not attempt to update
        references (they will be cascade-deleted)
        """
        exercise_to_delete = Exercise.objects.get(pk=1)
        self.assertEqual(WorkoutLog.objects.filter(exercise=exercise_to_delete).count(), 4)

        exercise_to_delete.delete()

        # Workout logs for this exercise should be gone (cascade)
        self.assertEqual(WorkoutLog.objects.filter(exercise_id=1).count(), 0)

    def test_exercise_with_nonexistent_replaced_by(self):
        """
        Test that an entry is generated when an exercise is deleted and the replaced by is
        set correctly. If the UUID is not found in the DB, it's set to None
        """
        self.assertEqual(DeletionLog.objects.all().count(), 0)

        exercise = Exercise.objects.get(pk=1)
        exercise.delete(replace_by='12345678-1234-1234-1234-1234567890ab')

        # Exercise is deleted
        log = DeletionLog.objects.get(pk=1)

        self.assertEqual(log.model_type, DeletionLog.MODEL_EXERCISE)
        self.assertEqual(log.replaced_by, None)

    def test_translation(self):
        """
        Test that an entry is generated when a translation is deleted
        """
        self.assertEqual(DeletionLog.objects.all().count(), 0)

        translation = Translation.objects.get(pk=1)
        translation.delete()

        # Translation is deleted
        count = DeletionLog.objects.filter(
            model_type=DeletionLog.MODEL_TRANSLATION,
            uuid=translation.uuid,
        ).count()
        self.assertEqual(count, 1)
