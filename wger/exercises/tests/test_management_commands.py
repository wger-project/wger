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
from io import StringIO
from unittest.mock import patch

# Django
from django.core.management import call_command
from django.test import SimpleTestCase

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    Exercise,
    ExerciseBase,
)


class TestSyncManagementCommands(SimpleTestCase):
    @patch('wger.exercises.sync.handle_deleted_entries')
    @patch('wger.exercises.sync.sync_muscles')
    @patch('wger.exercises.sync.sync_languages')
    @patch('wger.exercises.sync.sync_exercises')
    @patch('wger.exercises.sync.sync_equipment')
    @patch('wger.exercises.sync.sync_categories')
    @patch('wger.exercises.sync.sync_licenses')
    def test_sync_exercises(
        self,
        mock_sync_licenses,
        mock_sync_categories,
        mock_sync_equipment,
        mock_sync_exercises,
        mock_sync_languages,
        mock_sync_muscles,
        mock_delete_entries,
    ):
        call_command('sync-exercises')

        mock_sync_licenses.assert_called()
        mock_sync_categories.assert_called()
        mock_sync_equipment.assert_called()
        mock_sync_exercises.assert_called()
        mock_sync_languages.assert_called()
        mock_sync_muscles.assert_called()
        mock_delete_entries.assert_called()

    @patch('wger.exercises.sync.download_exercise_images')
    def test_download_exercise_images(self, mock_download_exercise_images):
        call_command('download-exercise-images')

        mock_download_exercise_images.assert_called()

    @patch('wger.exercises.sync.download_exercise_videos')
    def test_download_exercise_videos(self, mock_download_exercise_videos):
        call_command('download-exercise-videos')

        mock_download_exercise_videos.assert_called()


class TestHealthCheckManagementCommands(WgerTestCase):
    def setUp(self):
        super().setUp()
        self.out = StringIO()

    def test_find_no_problems(self):
        call_command('exercises-health-check', stdout=self.out)
        self.assertEqual('', self.out.getvalue())

    def test_find_untranslated(self):
        Exercise.objects.get(pk=1).delete()
        Exercise.objects.get(pk=5).delete()

        call_command('exercises-health-check', stdout=self.out)
        self.assertIn(
            'Exercise acad3949-36fb-4481-9a72-be2ddae2bc05 has no translations!',
            self.out.getvalue(),
        )
        self.assertNotIn('-> deleted', self.out.getvalue())

    def atest_fix_untranslated(self):
        Exercise.objects.get(pk=1).delete()

        call_command('exercises-health-check', '--delete-untranslated', stdout=self.out)
        self.assertIn('-> deleted', self.out.getvalue())
        self.assertRaises(ExerciseBase.DoesNotExist, ExerciseBase.objects.get, pk=1)

    def test_find_no_english_translation(self):
        Exercise.objects.get(pk=1).delete()

        call_command('exercises-health-check', stdout=self.out)
        self.assertIn(
            'Exercise acad3949-36fb-4481-9a72-be2ddae2bc05 has no English translation!',
            self.out.getvalue(),
        )
        self.assertNotIn('-> deleted', self.out.getvalue())

    def test_fix_no_english_translation(self):
        Exercise.objects.get(pk=1).delete()

        call_command('exercises-health-check', '--delete-no-english', stdout=self.out)
        self.assertIn('-> deleted', self.out.getvalue())
        self.assertRaises(ExerciseBase.DoesNotExist, ExerciseBase.objects.get, pk=1)

    def test_find_duplicate_translations(self):
        exercise = Exercise.objects.get(pk=1)
        exercise.language_id = 3
        exercise.save()

        call_command('exercises-health-check', stdout=self.out)
        self.assertIn(
            'Exercise acad3949-36fb-4481-9a72-be2ddae2bc05 has duplicate translations!',
            self.out.getvalue(),
        )
        self.assertNotIn('-> deleted', self.out.getvalue())

    def test_fix_duplicate_translations(self):
        exercise = Exercise.objects.get(pk=1)
        exercise.language_id = 3
        exercise.save()

        call_command('exercises-health-check', '--delete-duplicate-translations', stdout=self.out)
        self.assertIn('Deleting all but first fr translation', self.out.getvalue())
        self.assertRaises(Exercise.DoesNotExist, Exercise.objects.get, pk=5)
