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
from django.core.cache import cache

from wger.core.models import Language
from wger.exercises.models import Exercise, ExerciseLanguageMapper
from wger.utils.cache import cache_mapper
from wger.manager.models import Workout, WorkoutLog
from wger.utils.cache import reset_workout_canonical_form, reset_workout_log
from wger.utils.cache import delete_template_fragment_cache


class Command(BaseCommand):
    '''
    Clears caches (HTML, etc.)
    '''

    option_list = BaseCommand.option_list + (
        make_option('--clear-template',
                    action='store_true',
                    dest='clear_template',
                    default=False,
                    help='Clear template caches'),

        make_option('--clear-workout-cache',
                    action='store_true',
                    dest='clear_workout',
                    default=False,
                    help='Clear the workout canonical view'),

        make_option('--clear-exercise-mapper',
                    action='store_true',
                    dest='clear_exercise_mapper',
                    default=False,
                    help='Clear the exercise language mapper cache'),
    )

    help = 'Clears the application cache. You *must* pass at least one option ' \
           'specifying what exactly you want to clear.'

    def handle(self, *args, **options):
        '''
        Process the options
        '''

        if not options['clear_template'] \
                and not options['clear_workout'] \
                and not options['clear_exercise_mapper']:
            raise CommandError('Please select what cache you need to delete, see help')

        # Exercises, cached template fragments
        if options['clear_template']:
            for user in User.objects.all():
                for entry in WorkoutLog.objects.dates('date', 'year'):
                    for month in range(1, 13):
                        # print("User {0}, year {1}, month {2}".format(user.pk, entry.year, month))
                        reset_workout_log(user.id, entry.year, month)

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

        # Exercise language mapper
        if options['clear_exercise_mapper']:
            for m in ExerciseLanguageMapper.objects.all():
                cache.delete(cache_mapper.get_exercise_language_mapper(m))
