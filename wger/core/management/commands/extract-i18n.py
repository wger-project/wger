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

from django.core.management.base import BaseCommand

from wger.core.models import RepetitionUnit
from wger.exercises.models import (
    ExerciseCategory,
    Muscle,
    Equipment
)


class Command(BaseCommand):
    '''
    Helper command to read out the strings to manually include in the .po files
    '''

    help = 'Read out all strings that have to be included manually in the .po file'

    def handle(self, **options):

        # Collect all translatable items
        out = []
        out += [i for i in ExerciseCategory.objects.all()]
        out += [i for i in Equipment.objects.all()]
        out += [i for i in Muscle.objects.all()]
        out += [i for i in RepetitionUnit.objects.all()]

        # Print the result
        for i in out:
            self.stdout.write('msgid "{0}"\n'
                              'msgstr ""\n\n'.format(i))
