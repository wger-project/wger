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
from wger.manager.models import (
    Setting,
    WorkoutLog,
)
from wger.utils.constants import ENGLISH_SHORT_NAME


class Command(BaseCommand):
    """
    Deletes all unused exercises
    """

    help = """Deletes all unused exercises from the database. After running this script, sync
            the database with ´python manage.py sync-exercises`
            """

    def handle(self, **options):
        # Collect all exercise bases that are not used in any workout or log entry
        out = f'{ExerciseBase.objects.all().count()} exercises currently in the database'
        self.stdout.write(out)

        bases = set(Setting.objects.all().values_list('exercise_base', flat=True))
        bases_logs = set(WorkoutLog.objects.all().values_list('exercise_base', flat=True))
        bases.update(bases_logs)

        # Ask for confirmation
        out = f'{len(bases)} exercises are in use, delete the rest?'
        self.stdout.write(out)
        response = ''
        while response not in ('y', 'n'):
            response = input('Type y to delete or n to exit: ')

        if response == 'y':
            ExerciseBase.objects.exclude(pk__in=bases).delete()
            out = self.style.SUCCESS('Done! You can now run python manage.py sync-exercises')
            self.stdout.write(out)
        else:
            out = self.style.SUCCESS('Exiting without deleting anything')
            self.stdout.write(out)
