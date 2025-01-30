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
from wger.exercises.models import (
    Exercise,
    Translation,
)


class Command(BaseCommand):
    """
    Alter the author name in the exercise models.
    """

    help = (
        'Used to alter exercise license authors\n'
        'Must provide at least the exercise base id using --exercise-base-id\n'
        'or the exercise id using --exercise-id.\n'
        'Must also provide the new author name using --author-name\n'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--author-name', action='store', dest='author_name', help='The name of the new author'
        )
        parser.add_argument(
            '--exercise-id',
            action='store',
            dest='exercise_id',
            help='The ID of the exercise base',
        )
        parser.add_argument(
            '--translation-id',
            action='store',
            dest='translation_id',
            help='The ID of the exercise',
        )

    def handle(self, **options):
        author_name = options['author_name']
        exercise_id = options['exercise_id']
        translation_id = options['translation_id']

        if author_name is None:
            self.print_error('Please enter an author name')
            return

        if exercise_id is None and translation_id is None:
            self.print_error('Please enter an exercise or translation ID')
            return

        if exercise_id is not None:
            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                self.print_error('Failed to find exercise base')
                return
            exercise.license_author = author_name
            exercise.save()

        if translation_id is not None:
            try:
                translation = Translation.objects.get(id=translation_id)
            except Translation.DoesNotExist:
                self.print_error('Failed to find exercise')
                return
            translation.license_author = author_name
            translation.save()

        self.stdout.write(self.style.SUCCESS('Exercise and/or translation has been updated'))

    def print_error(self, error_message):
        self.stdout.write(self.style.WARNING(f'{error_message}'))
