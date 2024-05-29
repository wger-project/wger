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
        count_base_logs = DeletionLog.objects.filter(
            model_type=DeletionLog.MODEL_BASE,
            uuid=base.uuid,
        ).count()
        log = DeletionLog.objects.get(pk=1)

        self.assertEqual(count_base_logs, 1)
        self.assertEqual(log.model_type, 'base')
        self.assertEqual(log.uuid, base.uuid)
        self.assertEqual(log.comment, 'Exercise base of An exercise')
        self.assertEqual(log.replaced_by, None)

        # All translations are also deleted
        count = DeletionLog.objects.filter(model_type=DeletionLog.MODEL_TRANSLATION).count()
        self.assertEqual(count, 2)

        # First translation
        log2 = DeletionLog.objects.get(pk=4)
        self.assertEqual(log2.model_type, 'translation')
        self.assertEqual(log2.uuid, UUID('9838235c-e38f-4ca6-921e-9d237d8e0813'))
        self.assertEqual(log2.comment, 'An exercise')
        self.assertEqual(log2.replaced_by, None)

        # Second translation
        log3 = DeletionLog.objects.get(pk=5)
        self.assertEqual(log3.model_type, 'translation')
        self.assertEqual(log3.uuid, UUID('13b532f9-d208-462e-a000-7b9982b2b53e'))
        self.assertEqual(log3.comment, 'Test exercise 123')
        self.assertEqual(log3.replaced_by, None)

    def test_base_with_replaced_by(self):
        """
        Test that an entry is generated when a base is deleted and the replaced by is
        set correctly
        """
        self.assertEqual(DeletionLog.objects.all().count(), 0)

        exercise = ExerciseBase.objects.get(pk=1)
        exercise.delete(replace_by='ae3328ba-9a35-4731-bc23-5da50720c5aa')

        # Base is deleted
        log = DeletionLog.objects.get(pk=1)

        self.assertEqual(log.model_type, 'base')
        self.assertEqual(log.uuid, exercise.uuid)
        self.assertEqual(log.replaced_by, UUID('ae3328ba-9a35-4731-bc23-5da50720c5aa'))

    def test_base_with_nonexistent_replaced_by(self):
        """
        Test that an entry is generated when a base is deleted and the replaced by is
        set correctly. If the UUID is not found in the DB, it's set to None
        """
        self.assertEqual(DeletionLog.objects.all().count(), 0)

        exercise = ExerciseBase.objects.get(pk=1)
        exercise.delete(replace_by='12345678-1234-1234-1234-1234567890ab')

        # Base is deleted
        log = DeletionLog.objects.get(pk=1)

        self.assertEqual(log.model_type, 'base')
        self.assertEqual(log.replaced_by, None)

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
