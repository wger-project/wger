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
from wger.exercises.models.image import ExerciseImage
from wger.exercises.models.video import ExerciseVideo
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
        log = DeletionLog.objects.get(
            model_type=DeletionLog.MODEL_EXERCISE,
            uuid=exercise.uuid,
        )
        self.assertEqual(log.comment, 'Exercise base of An exercise')
        self.assertEqual(log.replaced_by, None)

        # All translations are also deleted
        translation_logs = DeletionLog.objects.filter(
            model_type=DeletionLog.MODEL_TRANSLATION,
        ).order_by('uuid')
        self.assertEqual(translation_logs.count(), 2)

        log2 = translation_logs.get(uuid=UUID('13b532f9-d208-462e-a000-7b9982b2b53e'))
        self.assertEqual(log2.comment, 'Test exercise 123')
        self.assertEqual(log2.replaced_by, None)

        log3 = translation_logs.get(uuid=UUID('9838235c-e38f-4ca6-921e-9d237d8e0813'))
        self.assertEqual(log3.comment, 'An exercise')
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
        log = DeletionLog.objects.get(
            model_type=DeletionLog.MODEL_EXERCISE,
            uuid=exercise.uuid,
        )
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

    def test_exercise_replace_by_transfers_media(self):
        """
        Test that images and videos of the deleted exercise are reassigned to
        the replacement when transfer_media is set.
        """
        exercise_to_delete = Exercise.objects.get(pk=1)
        replacement = Exercise.objects.get(pk=2)

        self.assertEqual(ExerciseImage.objects.filter(exercise=exercise_to_delete).count(), 2)
        self.assertEqual(ExerciseImage.objects.filter(exercise=replacement).count(), 1)
        self.assertEqual(ExerciseVideo.objects.filter(exercise=exercise_to_delete).count(), 2)
        self.assertEqual(ExerciseVideo.objects.filter(exercise=replacement).count(), 1)

        exercise_to_delete.delete(replace_by=str(replacement.uuid), transfer_media=True)

        self.assertEqual(ExerciseImage.objects.filter(exercise=replacement).count(), 3)
        self.assertEqual(ExerciseVideo.objects.filter(exercise=replacement).count(), 3)

    def test_exercise_replace_by_does_not_transfer_media_by_default(self):
        """
        Test that images and videos are cascade-deleted with the exercise when
        transfer_media is not set, even if a replacement is provided.
        """
        exercise_to_delete = Exercise.objects.get(pk=1)
        replacement = Exercise.objects.get(pk=2)

        self.assertEqual(ExerciseImage.objects.filter(exercise=replacement).count(), 1)
        self.assertEqual(ExerciseVideo.objects.filter(exercise=replacement).count(), 1)

        exercise_to_delete.delete(replace_by=str(replacement.uuid))

        self.assertEqual(ExerciseImage.objects.filter(exercise=replacement).count(), 1)
        self.assertEqual(ExerciseVideo.objects.filter(exercise=replacement).count(), 1)

    def test_exercise_replace_by_transfers_translations_in_missing_languages(self):
        """
        Test that translations of the deleted exercise whose language is not
        yet present on the replacement are reassigned. Translations in
        languages already present on the replacement are cascade-deleted.
        """
        exercise_to_delete = Exercise.objects.get(pk=1)
        replacement = Exercise.objects.get(pk=2)

        # ex1 has lang 2 ("An exercise", pk=1) and lang 3 ("Test exercise 123", pk=5)
        # ex2 has lang 2 ("Very cool exercise", pk=2)
        self.assertEqual(set(replacement.translations.values_list('language_id', flat=True)), {2})

        exercise_to_delete.delete(replace_by=str(replacement.uuid), transfer_translations=True)

        replacement.refresh_from_db()
        languages_on_replacement = set(
            replacement.translations.values_list('language_id', flat=True)
        )
        self.assertEqual(languages_on_replacement, {2, 3})

        # The lang 3 translation moved over (pk preserved)
        moved = Translation.objects.get(pk=5)
        self.assertEqual(moved.exercise_id, replacement.pk)
        self.assertEqual(moved.name, 'Test exercise 123')

        # The lang 2 translation on the source was cascade-deleted
        self.assertFalse(Translation.objects.filter(pk=1).exists())

    def test_exercise_replace_by_does_not_transfer_translations_by_default(self):
        """
        Test that translations are cascade-deleted with the exercise when
        transfer_translations is not set, even with a replacement.
        """
        exercise_to_delete = Exercise.objects.get(pk=1)
        replacement = Exercise.objects.get(pk=2)

        exercise_to_delete.delete(replace_by=str(replacement.uuid))

        replacement.refresh_from_db()
        languages_on_replacement = set(
            replacement.translations.values_list('language_id', flat=True)
        )
        self.assertEqual(languages_on_replacement, {2})

    def test_exercise_replace_by_transfer_flags_ignored_without_replacement(self):
        """
        Test that transfer flags have no effect if no replacement is given —
        everything cascades as usual.
        """
        exercise_to_delete = Exercise.objects.get(pk=1)
        exercise_to_delete.delete(transfer_media=True, transfer_translations=True)

        self.assertFalse(Exercise.objects.filter(pk=1).exists())
        self.assertEqual(ExerciseImage.objects.filter(exercise_id=1).count(), 0)
        self.assertEqual(ExerciseVideo.objects.filter(exercise_id=1).count(), 0)

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
        log = DeletionLog.objects.get(
            model_type=DeletionLog.MODEL_EXERCISE,
            uuid=exercise.uuid,
        )
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

    def test_exercise_delete_with_existing_deletion_log(self):
        """
        Test that re-deleting an exercise whose UUID already has a deletion log
        entry (e.g. it was deleted before, then re-imported via sync) updates
        the existing entry instead of raising an IntegrityError.
        """
        exercise = Exercise.objects.get(pk=1)
        DeletionLog.objects.create(
            model_type=DeletionLog.MODEL_EXERCISE,
            uuid=exercise.uuid,
            comment='stale entry from a previous deletion',
        )

        exercise.delete()

        log = DeletionLog.objects.get(uuid=exercise.uuid)
        self.assertEqual(log.model_type, DeletionLog.MODEL_EXERCISE)
        self.assertEqual(log.comment, 'Exercise base of An exercise')

    def test_translation_delete_with_existing_deletion_log(self):
        """
        Test that re-deleting a translation whose UUID already has a deletion log
        entry updates the existing entry instead of raising an IntegrityError.
        """
        translation = Translation.objects.get(pk=1)
        DeletionLog.objects.create(
            model_type=DeletionLog.MODEL_TRANSLATION,
            uuid=translation.uuid,
            comment='stale entry',
        )

        translation.delete()

        log = DeletionLog.objects.get(uuid=translation.uuid)
        self.assertEqual(log.model_type, DeletionLog.MODEL_TRANSLATION)
        self.assertEqual(log.comment, translation.name)
