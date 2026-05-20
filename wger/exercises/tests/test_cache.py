# Standard Library
from unittest.mock import (
    MagicMock,
    patch,
)

# Django
from django.test import override_settings

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.api.serializers import ExerciseInfoSerializer
from wger.exercises.cache import (
    cache_api_exercises,
    cache_exercise,
)
from wger.exercises.models import (
    Exercise,
    ExerciseImage,
)


class TestCacheExercise(WgerTestCase):
    @patch('wger.exercises.cache.reset_exercise_api_cache')
    @patch('wger.exercises.cache.ExerciseInfoSerializer')
    def test_cache_exercise_force_true(self, mock_serializer, mock_reset_cache):
        exercise = Exercise.objects.first()
        output = []

        serializer_instance = MagicMock()
        serializer_instance.data = {'mocked': True}
        mock_serializer.return_value = serializer_instance

        cache_exercise(exercise, force=True, print_fn=output.append)

        mock_reset_cache.assert_called_once_with(exercise.uuid)
        mock_serializer.assert_called_once_with(exercise)
        self.assertTrue(any('Force updating cache' in msg for msg in output))

    @patch('wger.exercises.cache.reset_exercise_api_cache')
    @patch('wger.exercises.cache.ExerciseInfoSerializer')
    def test_cache_exercise_force_false(self, mock_serializer, mock_reset_cache):
        exercise = Exercise.objects.first()
        output = []

        serializer_instance = MagicMock()
        serializer_instance.data = {'mocked': True}
        mock_serializer.return_value = serializer_instance

        cache_exercise(exercise, force=False, print_fn=output.append)

        mock_reset_cache.assert_not_called()
        mock_serializer.assert_called_once_with(exercise)
        self.assertTrue(any('Warming cache' in msg for msg in output))

    @patch('wger.exercises.cache.cache_exercise')
    def test_cache_api_exercises_calls_all(self, mock_cache_exercise):
        output = []
        called_exercises = []

        def fake_cache(exercise, force, print_fn, style_fn):
            called_exercises.append(exercise)

        mock_cache_exercise.side_effect = fake_cache
        cache_api_exercises(print_fn=output.append, force=True)

        self.assertTrue(len(called_exercises) > 0)

    @override_settings(SITE_URL='https://example.com')
    def test_cached_media_urls_are_absolute(self):
        """
        Media URLs are absolute even when the serializer has no request.

        The exercise cache is warmed by a celery task, which has no HTTP request
        to build absolute URLs from. Without the SITE_URL fallback the cached
        representation would carry host-less media paths.
        """
        exercise = ExerciseImage.objects.first().exercise

        data = ExerciseInfoSerializer(exercise).data

        self.assertTrue(data['images'], 'exercise needs at least one image')
        for image in data['images']:
            self.assertTrue(
                image['image'].startswith('https://example.com/'),
                f'Image URL is not absolute: {image["image"]}',
            )

        for video in data['videos']:
            self.assertTrue(
                video['video'].startswith('https://example.com/'),
                f'Video URL is not absolute: {video["video"]}',
            )

        for muscle in data['muscles']:
            self.assertTrue(
                muscle['image_url_main'].startswith('https://example.com/'),
                f'Muscle image URL is not absolute: {muscle["image_url_main"]}',
            )
