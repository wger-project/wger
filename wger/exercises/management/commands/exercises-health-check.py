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
from argparse import RawTextHelpFormatter

# Django
from django.core.management.base import BaseCommand

# wger
from wger.core.models import Language
from wger.exercises.models import Exercise
from wger.utils.constants import ENGLISH_SHORT_NAME


class Command(BaseCommand):
    """
    Performs some sanity checks on the exercise database
    """

    english: Language

    help = (
        'Performs some sanity checks on the exercise database. '
        'At the moment this script checks that each exercise:\n'
        '- has at least one translation\n'
        '- has a translation in English\n'
        '- has no duplicate translations\n\n'
        'Each problem can be fixed individually by using the --delete-* flags\n'
    )

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-untranslated',
            action='store_true',
            dest='delete_untranslated',
            default=False,
            help="Delete exercises without translations (safe to use since these can't be "
            'accessed over the UI)',
        )

        parser.add_argument(
            '--delete-no-english',
            action='store_true',
            dest='delete_no_english',
            default=False,
            help='Delete exercises without a fallback English translations',
        )

        parser.add_argument(
            '--delete-all',
            action='store_true',
            dest='delete_all',
            default=False,
            help='Sets all deletion flags to true',
        )

    def handle(self, **options):
        delete_untranslated = options['delete_untranslated'] or options['delete_all']
        delete_no_english = options['delete_no_english'] or options['delete_all']

        self.english = Language.objects.get(short_name=ENGLISH_SHORT_NAME)

        for exercise in Exercise.objects.all():
            self.handle_untranslated(exercise, delete_untranslated)
            self.handle_no_english(exercise, delete_no_english)

    def handle_untranslated(self, exercise: Exercise, delete: bool):
        """
        Delete exercises without translations
        """
        if not exercise.pk or exercise.translations.count():
            return

        self.stdout.write(self.style.WARNING(f'Exercise {exercise.uuid} has no translations!'))
        if delete:
            exercise.delete()
            self.stdout.write('  -> deleted')

    def handle_no_english(self, exercise: Exercise, delete: bool):
        if not exercise.pk or exercise.translations.filter(language=self.english).exists():
            return

        self.stdout.write(
            self.style.WARNING(f'Exercise {exercise.uuid} has no English translation!')
        )
        if delete:
            exercise.delete()
            self.stdout.write('  -> deleted')
