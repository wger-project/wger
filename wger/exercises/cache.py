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
from typing import Callable

# wger
from wger.exercises.api.serializers import ExerciseInfoSerializer
from wger.exercises.models import Exercise
from wger.utils.cache import reset_exercise_api_cache


def cache_exercise(
    exercise: Exercise, force=False, print_fn: Callable = print, style_fn: Callable = lambda x: x
):
    """
    Caches a provided exercise.
    """
    if force:
        print_fn(f'Force updating cache for exercise {exercise.uuid}')
        reset_exercise_api_cache(exercise.uuid)
    else:
        print_fn(f'Warming cache for exercise {exercise.uuid}')

    serializer = ExerciseInfoSerializer(exercise)
    serializer.data


def cache_api_exercises(
    print_fn: Callable,
    force: bool,
    style_fn: Callable = lambda x: x,
):
    print_fn('*** Caching API exercises ***')
    for exercise in Exercise.with_translations.all():
        cache_exercise(exercise, force, print_fn, style_fn)
    print_fn(style_fn('Exercises cached!\n'))
