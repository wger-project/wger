# -*- coding: utf-8 *-*

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

import datetime

from django.utils.timezone import now
from django.core.management.base import BaseCommand
from wger.exercises.models import ExerciseCategory


class Command(BaseCommand):
    '''
    Helper command to read out the exercise categories to manually include in
    the .po files
    '''

    help = 'Read the exercise categories to include in .po file'

    def handle(self, *args, **options):

        categories = ExerciseCategory.objects.all()
        for category in categories:
                self.stdout.write('msgid "{0}"\n'
                                  'msgstr ""\n\n'.format(category))
