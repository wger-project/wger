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
from wger.exercises.cache import cache_exercise
from wger.exercises.models import Exercise


class Command(BaseCommand):
    """
    Calls the exercise api to get all exercises and caches them in the database.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--exercise-id',
            action='store',
            dest='exercise_id',
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
        exercise_id = options['exercise_id']
        force = options['force']

        if exercise_id:
            exercise = Exercise.objects.get(pk=exercise_id)
            cache_exercise(exercise, force, self.stdout.write)
            return

        for exercise in Exercise.with_translations.all():
            cache_exercise(exercise, force, self.stdout.write)
