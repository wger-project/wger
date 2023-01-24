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
from wger.exercises.models import (
    DeletionLog,
    Exercise,
    ExerciseBase,
)


class DeletionLogTestCase(WgerTestCase):
    """
    Test that the deletion log entries are correctly generated
    """

    def test_base(self):
        """
        Test that an entry is generated when a base is deleted
        """
        self.assertEqual(DeletionLog.objects.all().count(), 0)

        base = ExerciseBase.objects.get(pk=1)
        base.delete()

        # Base is deleted
        count_base = DeletionLog.objects.filter(model_type=DeletionLog.MODEL_BASE,
                                                uuid=base.uuid).count()
        self.assertEqual(count_base, 1)

        # All translations are also deleted
        count = DeletionLog.objects.filter(model_type=DeletionLog.MODEL_TRANSLATION).count()
        self.assertEqual(count, 2)

    def test_translation(self):
        """
        Test that an entry is generated when a translation is deleted
        """
        self.assertEqual(DeletionLog.objects.all().count(), 0)

        translation = Exercise.objects.get(pk=1)
        translation.delete()

        # Translation is deleted
        count = DeletionLog.objects.filter(
            model_type=DeletionLog.MODEL_TRANSLATION, uuid=translation.uuid
        ).count()
        self.assertEqual(count, 1)
