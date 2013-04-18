# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import logging
import random
import datetime

from django.utils.translation import ugettext as _

from wger.weight.models import WeightEntry
from wger.exercises.models import Exercise
from wger.manager.models import DaysOfWeek
from wger.manager.models import Workout
from wger.manager.models import Day
from wger.manager.models import Set
from wger.manager.models import Setting
from wger.manager.models import WorkoutLog

from wger.utils.language import load_language

logger = logging.getLogger('workout_manager.custom')


def create_demo_workout(user):
    '''
    Creates some demo data for temporary users
    '''

    # (this is a bit ugly...)

    #
    # Workout and exercises
    #
    workout = Workout(user=user, comment=_('Sample workout'))
    workout.save()
    monday = DaysOfWeek.objects.get(pk=1)
    wednesday = DaysOfWeek.objects.get(pk=3)
    day = Day(training=workout, description=_('Sample day'))
    day.save()
    day.day.add(monday)

    day2 = Day(training=workout, description=_('Another sample day'))
    day2.save()
    day2.day.add(wednesday)

    # Biceps curls with dumbbell
    if(load_language().short_name == 'de'):
        exercise = Exercise.objects.get(pk=26)
    else:
        exercise = Exercise.objects.get(pk=81)
    day_set = Set(exerciseday=day, sets=4, order=2)
    day_set.save()
    day_set.exercises.add(exercise)

    setting = Setting(set=day_set, exercise=exercise, reps=8, order=1)
    setting.save()

    # Weight log entries
    for reps in (7, 8, 9, 10):
        for i in range(1, 8):
            log = WorkoutLog(user=user,
                             exercise=exercise,
                             workout=workout,
                             reps=reps,
                             weight=30 - reps + random.randint(1, 5),
                             date=datetime.date.today() - datetime.timedelta(weeks=i))
            log.save()

    # French press
    if(load_language().short_name == 'de'):
        exercise = Exercise.objects.get(pk=25)
    else:
        exercise = Exercise.objects.get(pk=84)
    day_set = Set(exerciseday=day, sets=4,  order=2)
    day_set.save()
    day_set.exercises.add(exercise)

    setting = Setting(set=day_set, exercise=exercise, reps=8, order=1)
    setting.save()

    # Squats
    if(load_language().short_name == 'de'):
        exercise = Exercise.objects.get(pk=6)
    else:
        exercise = Exercise.objects.get(pk=111)
    day_set = Set(exerciseday=day, sets=4, order=3)
    day_set.save()
    day_set.exercises.add(exercise)

    setting = Setting(set=day_set, exercise=exercise, reps=10, order=1)
    setting.save()

    # Crunches
    if(load_language().short_name == 'de'):
        exercise = Exercise.objects.get(pk=4)
    else:
        exercise = Exercise.objects.get(pk=91)
    day_set = Set(exerciseday=day, sets=4, order=4)
    day_set.save()
    day_set.exercises.add(exercise)

    setting = Setting(set=day_set, exercise=exercise, reps=30, order=1)
    setting.save()

    setting = Setting(set=day_set, exercise=exercise, reps=99, order=2)
    setting.save()

    setting = Setting(set=day_set, exercise=exercise, reps=35, order=3)
    setting.save()

    #
    # (Body) weight entries
    #
    for i in range(1, 20):
        creation_date = datetime.date.today() - datetime.timedelta(days=i)
        entry = WeightEntry(user=user,
                            weight=80 + 0.5*i + random.randint(1, 3),
                            creation_date=creation_date)
        entry.save()
