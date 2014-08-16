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
import decimal
import logging

from wger.exercises.models import ExerciseLanguageMapper
from wger.utils.constants import TWOPLACES

logger = logging.getLogger('wger.custom')

'''
Base automatic weightlifting routine generator classes.
'''


class Routine(object):
    '''
    Routine
    '''
    routines = {}
    exercise_configs = []
    weeks = 8
    description = ''
    name = ''
    short_name = ''
    user_config = {'round_to': 2.5,
                   'max_squat': 100,
                   'max_bench': 100,
                   'max_deadlift': 100}

    def __init__(self, weeks=8, name='', short_name='', description=''):
        self.weeks = weeks
        self.name = name
        self.short_name = short_name
        self.description = description
        self.routines = {}
        self.exercise_configs = []

        # Initialise the routines dictionary
        for week in range(1, self.weeks + 1):
            self.routines[week] = {}
            for day in range(1, 8):
                self.routines[week][day] = {}

    def __iter__(self):
        '''
        Iterate over the exercises and generate the complete routine
        '''
        out = self.prepare_sets()

        for week in sorted(out):
            for day in sorted(out[week]):
                for i in out[week][day]:
                    yield i

    def set_user_config(self, config):
        '''
        Sets the config dictionary (max bench, target bench, etc.).

        This is passed each exercise
        '''
        self.user_config = config

    @staticmethod
    def round_weight(weight, base=2.5):
        '''
        Rounds the weights used for the generated routines depending on the use

        :param weight: the original weight
        :param base: the base to round to
        :return: a rounded decimal
        '''
        return decimal.Decimal(base * round(float(weight)/base)).quantize(TWOPLACES)

    def prepare_sets(self):
        '''
        Prepares the sets so that they can be more easily displayed.

        At the moment this method only collapses sets with the same repetitions
        and weight (2x100, 2x100, 2x100 --> (3 x 2 100kg)

        :return: a dictionary with the reduced sets
        '''

        out = {}
        for week in sorted(self.routines):
            out[week] = {}
            for day in sorted(self.routines[week]):

                out[week][day] = []
                tmp = {}
                for set_nr in sorted(self.routines[week][day]):
                    exercise_config = self.routines[week][day][set_nr]
                    exercise_config.current_week = week
                    exercise_config.current_day = day
                    exercise_config.current_set = set_nr
                    exercise_config.set_user_config(self.user_config)

                    reps, weight = exercise_config.get_routine()

                    # Round weight to something usable
                    weight = self.round_weight(weight, self.user_config['round_to'])

                    if not tmp.get((exercise_config.name, reps, weight)):
                        tmp[(exercise_config.name, reps, weight)] = {'sets': 1,
                                                                     'set_nr': set_nr,
                                                                     'reps': reps,
                                                                     'weight': weight,
                                                                     'config': exercise_config}
                    else:
                        tmp[(exercise_config.name, reps, weight)]['sets'] += 1

                # Sorting by the set number because that allows us to sort the
                # exercises according to the order defined in the exercise config
                for value in sorted(tmp.values(), key=lambda k: k['set_nr']):
                    out[week][day].append({'week': week,
                                           'day': day,
                                           'sets': value['sets'],
                                           'weight': value['weight'],
                                           'reps': value['reps'],
                                           'exercise': value['config']})
        return out

    def add(self, exercise_config):
        '''
        Add an exercise to this routine
        :param exercise_config:
        '''
        self.exercise_configs.append(exercise_config)

        # See when the exercise provides data and add that to the general list
        for week in exercise_config.data:
            for day in exercise_config.data[week]:
                for set_nr in exercise_config.data[week][day]:
                    if self.routines[week][day].get(set_nr):
                        raise KeyError('Set has already data')
                    self.routines[week][day][set_nr] = exercise_config

    def check_plausibility(self):
        '''
        Performs some sanity checks on the workout data, e.g. that there are no
        'gaps' in the sets
        '''
        for config in self:
            pass
        return True


class ExerciseConfig(object):
    '''
    Exercise object used to generate Routines
    '''

    name = ''
    exercise_mapper = None
    user = None
    current_week = 0
    current_day = 0
    current_set = 0
    user_config = {}

    data = {}
    '''
    A dictionary of dictionaries specifying when this exercise configuration
    will provide data (from get_routine).

    The expected format is as follows:
    {
        week_nr1: {day_nr1: [set_nr1, set_nr2, set_nr3],
                   day_nr2: [...]},
        week_nr2: {...}
    }
    '''

    def __init__(self, name, mapper_pk):
        self.name = name
        self.exercise_mapper = ExerciseLanguageMapper.objects.get(pk=mapper_pk)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.name

    def set_user_config(self, config):
        '''
        Sets the config dictionary (max bench, target bench, etc.)
        '''
        self.user_config = config

    def get_routine(self):
        '''
        Generates the actual routine.

        When this function is called, the exercise has access to the current
        point in time (week, day and set) as well as the current user. It can
        perform any calculations needed to generate the weight and the repetitions
        for the set.

        In case the weight is not important or not provided by the routine (e.g.
        for other, not important exercises), the special value 'auto' might be
        returned for the weight.

        :return: a tuple with the number of sets and the weight
        '''
        raise NotImplementedError
