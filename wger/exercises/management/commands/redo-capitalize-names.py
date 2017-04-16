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

from wger.exercises.models import Exercise
from wger.utils.helpers import smart_capitalize


class Command(BaseCommand):
    '''
    Re-calculates the capitalized exercise names

    This is a safe operation, since the original names (as entered by the user)
    are still available.
    '''

    help = 'Re-calculates the capitalized exercise names'

    def handle(self, **options):

        exercises = Exercise.objects.all()
        for exercise in exercises:
            if options['verbosity'] > 1:
                self.stdout.write('#{} {} -> {}'.format(exercise.id,
                                                        exercise.name,
                                                        smart_capitalize(exercise.name_original)))
            exercise.name = smart_capitalize(exercise.name_original)
            exercise.save()
