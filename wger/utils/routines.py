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
import math
from django.core.exceptions import ImproperlyConfigured

from django.utils.translation import ugettext as _
from wger.exercises.models import ExerciseLanguageMapper
from wger.utils.constants import TWOPLACES, FOURPLACES

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
    name = ''
    '''
    Name of the routine
    '''

    slug = ''
    '''
    URL friendly name
    '''

    description = ''
    '''
    Description
    '''

    user_config = {}

    def __init__(self, weeks=8, name='', slug='', description=''):
        self.weeks = weeks
        self.name = name
        self.slug = slug
        self.description = description
        self.routines = {}
        self.exercise_configs = []

    def __iter__(self):
        '''
        Iterate over the exercises and generate the complete routine
        '''
        out = self.get_data_list()

        for week in sorted(out):
            for day in sorted(out[week]):
                for set_nr in out[week][day]:
                    config = out[week][day][set_nr]
                    config.set_current_step(week, day, set_nr)
                    yield config.get_routine_data()

    def set_user_config(self, config):
        '''
        Sets the config dictionary (max bench, target bench, etc.).

        This is passed to each exercise
        '''
        self.user_config = config

    def get_data_list(self):
        '''
        Convenience method that returns a list with the weeks, days and sets
        for which this routine has data
        '''
        out = {}
        for exercise in self.exercise_configs:
            for config in exercise.configs:
                config.set_user_config(self.user_config)
                data = config.get_data_list()
                for week in data:
                    if not out.get(week):
                        out[week] = {}

                    for day in data[week]:

                        if not out[week].get(day):
                            out[week][day] = {}

                        for set_nr in data[week][day]:
                            if out[week][day].get(set_nr):
                                raise KeyError('Set has already data: week {0} day {1} set {2}'
                                               .format(week, day, set_nr))

                            out[week][day][set_nr] = config
        return out

    @staticmethod
    def round_weight(weight, base=2.5):
        '''
        Rounds the weights used for the generated routines depending on the use

        :param weight: the original weight
        :param base: the base to round to
        :return: a rounded python decimal with two decimal places
        '''
        if weight in ('auto', 'max'):
            return weight
        return decimal.Decimal(base * round(float(weight)/base)).quantize(TWOPLACES)

    def add(self, exercise_config):
        '''
        Add an exercise to this routine
        :param exercise_config:
        '''
        self.exercise_configs.append(exercise_config)
        self.routines = self.get_data_list()

    def check_plausibility(self):
        '''
        Performs some sanity checks on the workout data, e.g. that there are no
        'gaps' in the sets
        '''
        for config in self:
            pass
            #  raise ValueError('Please check the routine')


class RoutineExercise(object):
    '''
    Simple wrapper around the exercise configs belonging to a routine
    '''

    configs = []
    exercise_mapper = None
    responsibility = {}

    def __init__(self, mapper_pk):
        self.exercise_mapper = ExerciseLanguageMapper.objects.get(pk=mapper_pk)
        self.configs = []

    def add_config(self, config):
        '''
        Adds an exercise config
        '''
        config.set_routine_exercise(self)
        self.configs.append(config)

    def get_data_list(self):
        '''
        Convenience method that returns a list with the weeks, days and sets
        for which this exercise is responsible
        '''

        out = {}
        for config in self.configs:
            data = config.get_data_list()
            for week in data:
                if not out.get(week):
                    out[week] = {}

                for day in data[week]:

                    if not out[week].get(day):
                        out[week][day] = {}

                    for set_nr in data[week][day]:

                        if out[week][day].get(set_nr):
                            raise KeyError('Set has already data')

                        out[week][day][set_nr] = config

        self.responsibility = out
        return out


class ExerciseConfig(object):
    '''
    Exercise weight configuration used to generate Routines
    '''

    current_week = 0
    current_day = 0
    current_set = 0
    user_config = {}
    routine_exercise = None

    reps = 0
    '''
    The number of repetitions
    '''

    sets = 0
    '''
    The number of sets
    '''

    increment_mode = 'static'
    '''
    Main weight increment mode

    Possible values:
    * 'static': weight increases by a static amount each week
    * 'dynamic': weight increase depends on user's performance
    * 'manual': manual, will be returned by get_routine
    '''

    start_weight = 0
    '''
    The weight at the start. Not needed for manual mode.
    '''

    unit = 'kg'
    '''
    The unit used for the weight increases

    Possible values:
    * 'kg'
    * 'lb'
    * 'percent'
    '''

    increment = 0
    '''
    The weekly weight increase
    '''

    responsibility = {}
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

    def __init__(self):
        self.user_config = {}

        if self.unit == 'percent' and (self.increment < 0 or self.increment > 10):
            raise ValueError('Percentage must be between 0 and 10')

    def set_routine_exercise(self, routine_exercise):
        '''
        Sets the routine exercise object
        :param routine_exercise:
        '''
        self.routine_exercise = routine_exercise

    def set_current_step(self, week, day, set_nr):
        '''
        Sets the current step
        '''
        self.current_week = week
        self.current_day = day
        self.current_set = set_nr

    def get_data_list(self):
        '''
        Convenience method that returns a list with the weeks, days and sets
        for which this config is responsible
        '''
        return self.responsibility

    def set_user_config(self, config):
        '''
        Sets the user config dictionary (max bench, target bench, etc.)
        '''
        self.user_config = config

    def get_step(self, week, day, set_nr):
        '''
        Returns the 'step' for the week, day and set (how often this config
        was used). This function is used for automatic weight calculation
        that increase each time

        :return: integer or None if values not in config's responsibility
        '''
        try:
            if set_nr not in self.responsibility[week][day]:
                return None
        except KeyError:
            return None

        step = 1
        for current_week in self.responsibility:
            for current_day in self.responsibility[current_week]:
                for current_set in self.responsibility[current_week][current_day]:
                    if current_week == week and current_day == day and current_set == set_nr:
                        return step

                    step += 1

    def get_routine(self):
        '''

        :return:
        '''
        raise NotImplementedError

    def get_routine_data(self):
        '''
        Generates the actual routine.

        When this function is called, the exercise has access to the current
        point in time (week, day and set) as well as the current user. It can
        perform any calculations needed to generate the weight and the repetitions
        for the set.

        :return: a tuple with the number of sets and the weight
        '''
        if self.increment_mode == 'manual':
            reps, weight = self.get_routine()
            #

        # Automatic calculation
        elif self.increment_mode == 'static':
            step = self.get_step(self.current_week, self.current_day, self.current_set)
            if not step:
                raise KeyError("Config does not provide data for current step")

            if self.unit == 'percent':
                weight = self.start_weight * math.pow((100 + self.increment) / 100.0, step)
            else:
                #  TODO: unit (kg, lb)
                weight = self.start_weight + (step * self.increment)

            reps = self.reps
            weight = decimal.Decimal(weight).quantize(FOURPLACES)

        # Dynamic, depends on users past performance and can only be used when
        # imported into a schedule
        else:
            reps = self.reps
            weight = _(u'Dynamic value. Add to schedule.')

        return {'sets': self.sets,
                'current_week': self.current_week,
                'current_day': self.current_day,
                'current_set': self.current_set,
                'reps': reps,
                'weight': weight,
                'unit': self.unit,
                'increment_mode': self.increment_mode,
                'config': self}
