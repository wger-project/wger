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
from typing import Any

# Django
from django.core.management.base import BaseCommand

# Third Party
from tqdm import tqdm

# wger
from wger.manager.helpers import reset_routine_cache
from wger.manager.models import Routine


class Command(BaseCommand):
    help = 'Resets the cache for all routines.'

    def handle(self, *args, **options):
        total_routines = Routine.objects.count()
        self.stdout.write(f'Updating cache for {total_routines} routines...')

        with tqdm(total=total_routines, unit='routine', unit_scale=True) as pbar:
            routine: Routine
            for routine in Routine.objects.all():
                reset_routine_cache(routine)
                _ = routine.date_sequence
                pbar.update(1)

        self.stdout.write(self.style.SUCCESS('Successfully updated cache for all routines!'))
