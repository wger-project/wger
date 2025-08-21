# Standard Library
from unittest.mock import (
    MagicMock,
    patch,
)

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.cache import (
    cache_api_exercises,
    cache_exercise,
)
from wger.exercises.models import Exercise


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
