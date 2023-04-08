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
from unittest.mock import patch

# Django
from django.core.management import call_command
from django.test import SimpleTestCase


class TestManagementCommands(SimpleTestCase):

    @patch('wger.exercises.sync.delete_entries')
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
