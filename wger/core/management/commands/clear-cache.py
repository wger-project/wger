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

from optparse import make_option

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from wger.core.models import Language
from wger.manager.models import Workout, WorkoutLog
from wger.exercises.models import Exercise
from wger.utils.cache import (
    reset_workout_canonical_form,
    reset_workout_log,
    delete_template_fragment_cache
)


class Command(BaseCommand):
    '''
    Clears caches (HTML, etc.)
    '''

    option_list = BaseCommand.option_list + (
        make_option('--clear-template',
                    action='store_true',
                    dest='clear_template',
                    default=False,
                    help='Clear only template caches'),

        make_option('--clear-workout-cache',
                    action='store_true',
                    dest='clear_workout',
                    default=False,
                    help='Clear only the workout canonical view'),
    )

    help = 'Clears the application cache. You *must* pass an option selecting ' \
           'what exactly you want to clear. See available options.'

    def handle(self, *args, **options):
        '''
        Process the options
        '''

        if not options['clear_template'] and not options['clear_workout']:
            raise CommandError('Please select what cache you need to delete, see help')

        # Exercises, cached template fragments
        if options['clear_template']:
            if int(options['verbosity']) >= 2:
                self.stdout.write("*** Clearing templates")

            for user in User.objects.all():
                if int(options['verbosity']) >= 2:
                    self.stdout.write("* Processing user {0}".format(user.username))

                for entry in WorkoutLog.objects.filter(user=user).dates('date', 'year'):

                    if int(options['verbosity']) >= 3:
                        self.stdout.write("  Year {0}".format(entry.year))
                    for month in WorkoutLog.objects.filter(user=user,
                                                           date__year=entry.year).dates('date',
                                                                                        'month'):
                        if int(options['verbosity']) >= 3:
                            self.stdout.write("    Month {0}".format(entry.month))
                        reset_workout_log(user.id, entry.year, entry.month)
                        for day in WorkoutLog.objects.filter(user=user,
                                                             date__year=entry.year,
                                                             date__month=month.month).dates('date',
                                                                                            'day'):
                            if int(options['verbosity']) >= 3:
                                self.stdout.write("      Day {0}".format(day.day))
                            reset_workout_log(user.id, entry.year, entry.month, day)

            for language in Language.objects.all():
                delete_template_fragment_cache('muscle-overview', language.id)
                delete_template_fragment_cache('exercise-overview', language.id)
                delete_template_fragment_cache('exercise-overview-mobile', language.id)
                delete_template_fragment_cache('equipment-overview', language.id)

            for language in Language.objects.all():
                for exercise in Exercise.objects.all():
                    delete_template_fragment_cache('exercise-detail-header',
                                                   exercise.id,
                                                   language.id)
                    delete_template_fragment_cache('exercise-detail-muscles',
                                                   exercise.id,
                                                   language.id)
        # Workout canonical form
        if options['clear_workout']:
            for w in Workout.objects.all():
                reset_workout_canonical_form(w.pk)
