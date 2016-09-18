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


class Command(BaseCommand):
    '''
    Read out the user submitted exercise.

    Used to generate the AUTHORS file for a release
    '''

    help = 'Read out the user submitted exercise'

    def handle(self, **options):

        exercises = Exercise.objects.accepted()
        usernames = []
        for exercise in exercises:
            if exercise.user not in usernames:
                usernames.append(exercise.user)
                self.stdout.write(exercise.user)
