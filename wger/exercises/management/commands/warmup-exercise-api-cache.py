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

# Django
from django.core.management.base import BaseCommand

# wger
from wger.exercises.api.serializers import ExerciseBaseInfoSerializer
from wger.exercises.models import ExerciseBase
from wger.utils.cache import reset_exercise_api_cache


class Command(BaseCommand):
    """
    Calls the exercise api to get all exercises and caches them in the database.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--exercise-base-id',
            action='store',
            dest='exercise_base_id',
            help='The ID of the exercise base, otherwise all exercises will be updated',
        )

        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force the update of the cache',
        )

    def handle(self, **options):
        exercise_base_id = options['exercise_base_id']
        force = options['force']

        if exercise_base_id:
            exercise = ExerciseBase.objects.get(pk=exercise_base_id)
            self.handle_cache(exercise, force)
            return

        for exercise in ExerciseBase.translations.all():
            self.handle_cache(exercise, force)

    def handle_cache(self, exercise: ExerciseBase, force: bool):
        if force:
            self.stdout.write(f'Force updating cache for exercise base {exercise.uuid}')
        else:
            self.stdout.write(f'Warming cache for exercise base {exercise.uuid}')

        if force:
            reset_exercise_api_cache(exercise.uuid)

        serializer = ExerciseBaseInfoSerializer(exercise)
        serializer.data
