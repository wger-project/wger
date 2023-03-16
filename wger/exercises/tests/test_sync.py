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

# wger
from wger.core.models import Language
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    Equipment,
    Exercise,
    ExerciseBase,
    ExerciseCategory,
    Muscle,
)
from wger.exercises.sync import (
    delete_entries,
    sync_categories,
    sync_equipment,
    sync_languages,
    sync_muscles,
)
from wger.utils.requests import wger_headers


class MockLanguageResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b'1234'

    @staticmethod
    def json():
        return {
            "count": 24,
            "next": "http://localhost:8000/api/v2/language/?limit=20&offset=20",
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "short_name": "de",
                    "full_name": "Daitsch"
                }, {
                    "id": 2,
                    "short_name": "en",
                    "full_name": "English"
                }, {
                    "id": 3,
                    "short_name": "fr",
                    "full_name": "Français"
                }, {
                    "id": 4,
                    "short_name": "es",
                    "full_name": "Español"
                }, {
                    "id": 19,
                    "short_name": "eo",
                    "full_name": "Esperanto"
                }
            ]
        }


class MockCategoryResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b'1234'

    @staticmethod
    def json():
        return {
            "count": 6,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "name": "A cooler, swaggier category"
                }, {
                    "id": 2,
                    "name": "Another category"
                }, {
                    "id": 3,
                    "name": "Yet another category"
                }, {
                    "id": 4,
                    "name": "Calves"
                }, {
                    "id": 5,
                    "name": "Cardio"
                }, {
                    "id": 16,
                    "name": "Chest"
                }
            ]
        }


class MockMuscleResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b''

    @staticmethod
    def json():
        return {
            "count": 4,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "name": "Anterior testoid",
                    "name_en": "Testoulders",
                    "is_front": True,
                    "image_url_main": "/static/images/muscles/main/muscle-1.svg",
                    "image_url_secondary": "/static/images/muscles/secondary/muscle-1.svg"
                },
                {
                    "id": 2,
                    "name": "Novum musculus nomen eius",
                    "name_en": "Testceps",
                    "is_front": True,
                    "image_url_main": "/static/images/muscles/main/muscle-2.svg",
                    "image_url_secondary": "/static/images/muscles/secondary/muscle-2.svg"
                },
                {
                    "id": 3,
                    "name": "Biceps notusensis",
                    "name_en": "",
                    "is_front": False,
                    "image_url_main": "/static/images/muscles/main/muscle-3.svg",
                    "image_url_secondary": "/static/images/muscles/secondary/muscle-3.svg"
                },
                {
                    "id": 10,
                    "name": "Pectoralis major",
                    "name_en": "Chest",
                    "is_front": True,
                    "image_url_main": "/static/images/muscles/main/muscle-10.svg",
                    "image_url_secondary": "/static/images/muscles/secondary/muscle-10.svg"
                },
            ]
        }


class MockEquipmentResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b''

    @staticmethod
    def json():
        return {
            "count": 4,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "name": "Dumbbells"
                },
                {
                    "id": 2,
                    "name": "Kettlebell"
                },
                {
                    "id": 3,
                    "name": "A big rock"
                },
                {
                    "id": 42,
                    "name": "Gym mat"
                },
            ]
        }


class MockDeletionLogResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b''

    @staticmethod
    def json():
        return {
            "count": 4,
            "next": None,
            "previous": None,
            "results": [
                {
                    "model_type": "base",
                    "uuid": "acad394936fb44819a72be2ddae2bc05",
                    "timestamp": "2023-01-30T19:32:56.761426+01:00",
                    "comment": "Exercise base with ID 1"
                },
                {
                    "model_type": "translation",
                    "uuid": "0ef4cec8-d9c9-464f-baf9-3dbdf20083cb",
                    "timestamp": "2023-01-30T19:32:56.764582+01:00",
                    "comment": "Translation that is not in this DB"
                },
                {
                    "model_type": "translation",
                    "uuid": "946afe7b54a644a69c36c3e31e6b4c3b",
                    "timestamp": "2023-01-30T19:32:56.765350+01:00",
                    "comment": "Translation with ID 3"
                },
                {
                    "model_type": "foobar",
                    "uuid": "37b5813c76bd4658820a572d9dd93f31",
                    "timestamp": "2023-01-30T19:32:56.765350+01:00",
                    "comment": "UUID of existing translation but other model type"
                },
            ]
        }


class TestSyncMethods(WgerTestCase):

    @patch('requests.get', return_value=MockLanguageResponse())
    def test_language_sync(self, mock_request):
        self.assertEqual(Language.objects.count(), 3)
        self.assertEqual(Language.objects.get(pk=1).full_name, 'Deutsch')

        sync_languages(lambda x: x)
        mock_request.assert_called_with(
            'https://wger.de/api/v2/language/',
            headers=wger_headers(),
        )
        self.assertEqual(Language.objects.get(pk=1).full_name, 'Daitsch')
        self.assertEqual(Language.objects.get(pk=5).full_name, 'Esperanto')
        self.assertEqual(Language.objects.count(), 5)

    @patch('requests.get', return_value=MockCategoryResponse())
    def test_categories_sync(self, mock_request):
        self.assertEqual(ExerciseCategory.objects.count(), 4)
        self.assertEqual(ExerciseCategory.objects.get(pk=1).name, 'Category')

        sync_categories(lambda x: x)
        mock_request.assert_called_with(
            'https://wger.de/api/v2/exercisecategory/',
            headers=wger_headers(),
        )
        self.assertEqual(ExerciseCategory.objects.count(), 6)
        self.assertEqual(ExerciseCategory.objects.get(pk=1).name, 'A cooler, swaggier category')
        self.assertEqual(ExerciseCategory.objects.get(pk=16).name, 'Chest')

    @patch('requests.get', return_value=MockMuscleResponse())
    def test_muscle_sync(self, mock_request):
        self.assertEqual(Muscle.objects.count(), 6)
        self.assertEqual(Muscle.objects.get(pk=2).name, 'Biceps testii')
        self.assertFalse(Muscle.objects.get(pk=2).is_front)
        sync_muscles(lambda x: x)

        mock_request.assert_called_with(
            'https://wger.de/api/v2/muscle/',
            headers=wger_headers(),
        )
        self.assertEqual(Muscle.objects.count(), 7)
        self.assertTrue(Muscle.objects.get(pk=2).is_front)
        self.assertEqual(Muscle.objects.get(pk=2).name, 'Novum musculus nomen eius')
        self.assertEqual(Muscle.objects.get(pk=10).name, 'Pectoralis major')

    @patch('requests.get', return_value=MockEquipmentResponse())
    def test_equipment_sync(self, mock_request):
        self.assertEqual(Equipment.objects.count(), 3)
        self.assertEqual(Equipment.objects.get(pk=3).name, 'Something else')
        sync_equipment(lambda x: x)

        mock_request.assert_called_with(
            'https://wger.de/api/v2/equipment/',
            headers=wger_headers(),
        )
        self.assertEqual(Equipment.objects.count(), 4)
        self.assertEqual(Equipment.objects.get(pk=3).name, 'A big rock')
        self.assertEqual(Equipment.objects.get(pk=42).name, 'Gym mat')

    @patch('requests.get', return_value=MockDeletionLogResponse())
    def test_deletion_log(self, mock_request):
        self.assertEqual(ExerciseBase.objects.count(), 8)
        self.assertEqual(Exercise.objects.count(), 11)
        delete_entries(lambda x: x)

        mock_request.assert_called_with(
            'https://wger.de/api/v2/deletion-log/?limit=100',
            headers=wger_headers(),
        )
        self.assertEqual(ExerciseBase.objects.count(), 7)
        self.assertEqual(Exercise.objects.count(), 8)
        self.assertRaises(Exercise.DoesNotExist, Exercise.objects.get, pk=3)
        self.assertRaises(ExerciseBase.DoesNotExist, ExerciseBase.objects.get, pk=1)
