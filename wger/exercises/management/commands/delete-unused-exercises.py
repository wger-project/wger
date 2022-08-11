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
from wger.manager.models import Setting, WorkoutLog
from wger.utils.constants import ENGLISH_SHORT_NAME


class Command(BaseCommand):
    """
    Deletes all unused exercises
    """

    help = """Deletes all unused exercises from the database. After running this script, sync
            the database with ´python manage.py sync-exercises`
            """

    def handle(self, **options):

        out = f'{ExerciseBase.objects.all().count()} exercise bases currently in the database'
        self.stdout.write(out)

        bases = set(Setting.objects.all().values_list('exercise_base', flat=True))
        bases_logs = set(WorkoutLog.objects.all().values_list('exercise_base', flat=True))
        bases.update(bases_logs)

        out = f'-> {len(bases)} exercise bases are in use, deleting the rest'
        self.stdout.write(out)
        ExerciseBase.objects.exclude(pk__in=bases).delete()

        out = self.style.SUCCESS('Done! You can now run python manage.py sync-exercises')
        self.stdout.write(out)
