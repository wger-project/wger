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

from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    Exercise,
    Variation,
)


class CleanupOrphanedVariationsTestCase(WgerTestCase):
    """
    Test that the post_save signal on Exercise cleans up variation groups
    that have fewer than 2 exercises.
    """

    def test_removing_exercise_from_group_of_two_cleans_up(self):
        """
        When a group has 2 exercises and one is removed, the remaining
        exercise should be unlinked and the variation deleted.
        """
        # Variation 1 has 2 exercises in the test fixtures
        variation = Variation.objects.get(pk=1)
        members = Exercise.objects.filter(variations=variation)
        self.assertEqual(members.count(), 2)
        other_pk = members.exclude(pk=members.first().pk).first().pk

        # Remove one exercise from the group
        exercise = members.first()
        exercise.variations = None
        exercise.save()

        # The variation should be deleted and the other exercise unlinked
        self.assertFalse(Variation.objects.filter(pk=1).exists())
        other = Exercise.objects.get(pk=other_pk)
        self.assertIsNone(other.variations)

    def test_removing_exercise_from_larger_group_keeps_group(self):
        """
        When a group has 3+ exercises and one is removed, the group
        should remain intact.
        """
        # Add a third exercise to variation 1
        variation = Variation.objects.get(pk=1)
        ex = Exercise.objects.filter(variations__isnull=True).first()
        ex.variations = variation
        ex.save()
        self.assertEqual(
            Exercise.objects.filter(variations=variation).count(), 3
        )

        # Remove one exercise
        first = Exercise.objects.filter(variations=variation).first()
        first.variations = None
        first.save()

        # The group should still exist with 2 members
        self.assertTrue(Variation.objects.filter(pk=variation.pk).exists())
        self.assertEqual(
            Exercise.objects.filter(variations=variation).count(), 2
        )

    def test_moving_exercise_to_different_group_cleans_up_old(self):
        """
        When an exercise is moved from a 2-exercise group to another group,
        the old group should be cleaned up.
        """
        old_variation = Variation.objects.get(pk=1)
        new_variation = Variation.objects.get(pk=2)
        self.assertEqual(
            Exercise.objects.filter(variations=old_variation).count(), 2
        )

        # Move one exercise to the other group
        exercise = Exercise.objects.filter(variations=old_variation).first()
        exercise.variations = new_variation
        exercise.save()

        # Old variation should be cleaned up
        self.assertFalse(Variation.objects.filter(pk=old_variation.pk).exists())

    def test_saving_without_change_does_nothing(self):
        """
        Saving an exercise without changing its variation should not
        affect the group.
        """
        variation = Variation.objects.get(pk=2)
        count_before = Exercise.objects.filter(variations=variation).count()

        # Save without changing variation
        exercise = Exercise.objects.filter(variations=variation).first()
        exercise.save()

        # Nothing should change
        self.assertTrue(Variation.objects.filter(pk=variation.pk).exists())
        self.assertEqual(
            Exercise.objects.filter(variations=variation).count(),
            count_before,
        )
