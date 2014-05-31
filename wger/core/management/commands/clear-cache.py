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

from django.core.management.base import BaseCommand, CommandError

from wger.core.models import Language
from wger.manager.models import Workout
from wger.exercises.models import Exercise
from wger.utils.cache import reset_workout_canonical_form
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
            for language in Language.objects.all():
                delete_template_fragment_cache('muscle-overview', language.id)
                delete_template_fragment_cache('exercise-overview', language.id)
                delete_template_fragment_cache('exercise-overview-mobile', language.id)
                delete_template_fragment_cache('exercise-overview-search', language.id)
                delete_template_fragment_cache('equipment-overview', language.id)
                delete_template_fragment_cache('equipment-overview-mobile', language.id)

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
