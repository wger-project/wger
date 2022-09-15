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
import collections

# Django
from django.core.management.base import BaseCommand

# wger
from wger.core.models import Language
from wger.exercises.models import ExerciseBase
from wger.utils.constants import ENGLISH_SHORT_NAME


class Command(BaseCommand):
    """
    Performs some sanity checks on the exercise database
    """

    help = """Performs some sanity checks on the database

            At the moment this script checks the following:
            - each base has at least one exercise
            - each exercise base has a translation in English
            - exercise bases have no duplicate translations
            """

    def add_arguments(self, parser):

        # Add dry run argument
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete problematic exercise bases from the database (use with care!!)',
        )

    def handle(self, **options):

        delete = options['delete']
        english = Language.objects.get(short_name=ENGLISH_SHORT_NAME)

        for base in ExerciseBase.objects.all():

            if not base.exercises.count():
                warning = f'Exercise base {base.uuid} has no translations!'
                self.stdout.write(self.style.WARNING(warning))

                if delete:
                    base.delete()
                    self.stdout.write('  Deleting base...')
                continue

            if not base.exercises.filter(language=english).exists():
                warning = f'Exercise base {base.uuid} has no English translation!'
                self.stdout.write(self.style.WARNING(warning))

                if delete:
                    base.delete()
                    self.stdout.write('  Deleting base...')

            exercise_languages = base.exercises.values_list('language_id', flat=True)
            duplicates = [
                item for item, count in collections.Counter(exercise_languages).items() if count > 1
            ]

            if not duplicates:
                continue

            warning = f'Exercise base {base.uuid} has duplicate translations for language IDs: {duplicates}!'
            self.stdout.write(self.style.WARNING(warning))

            # Output the duplicates
            for language_id in duplicates:
                exercises = base.exercises.filter(language_id=language_id)
                self.stdout.write(f'Language {language_id}:')
                for exercise in exercises:
                    self.stdout.write(f'  * {exercise.name} (uuid: {exercise.uuid} )')
                self.stdout.write('')

            # And delete them
            exercises = base.exercises.filter(language_id__in=duplicates)
            if delete:
                for exercise in exercises[1:]:
                    self.stdout.write(
                        f'  Deleting translation {exercise.uuid} for language ID {exercise.language_id}...'
                    )
                    exercise.delete()
