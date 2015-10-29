# -*- coding: utf-8 -*-

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

import logging
import random
import datetime
import uuid

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _

from wger.weight.models import WeightEntry
from wger.exercises.models import Exercise
from wger.core.models import DaysOfWeek
from wger.manager.models import (
    Workout,
    Day,
    Set,
    Setting,
    WorkoutLog,
    Schedule,
    ScheduleStep
)
from wger.nutrition.models import (
    NutritionPlan,
    Meal,
    MealItem,
    Ingredient,
    IngredientWeightUnit
)

from wger.utils.language import load_language

logger = logging.getLogger(__name__)


def create_temporary_user():
    '''
    Creates a temporary user
    '''
    username = uuid.uuid4().hex[:-2]
    password = uuid.uuid4().hex[:-2]
    email = ''

    user = User.objects.create_user(username, email, password)
    user.save()
    user_profile = user.userprofile
    user_profile.is_temporary = True
    user_profile.age = 25
    user_profile.height = 175
    user_profile.save()
    user = authenticate(username=username, password=password)
    return user


def create_demo_entries(user):
    '''
    Creates some demo data for temporary users
    '''

    # (this is a bit ugly and long...)
    language = load_language()

    #
    # Workout and exercises
    #
    setting_list = []
    weight_log = []
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
    if language.short_name == 'de':
        exercise = Exercise.objects.get(pk=26)
    else:
        exercise = Exercise.objects.get(pk=81)
    day_set = Set(exerciseday=day, sets=4, order=2)
    day_set.save()
    day_set.exercises.add(exercise)

    setting = Setting(set=day_set, exercise=exercise, reps=8, order=1)
    setting.save()

    # Weight log entries
    for reps in (8, 10, 12):
        for i in range(1, 8):
            log = WorkoutLog(user=user,
                             exercise=exercise,
                             workout=workout,
                             reps=reps,
                             weight=18 - reps + random.randint(1, 4),
                             date=datetime.date.today() - datetime.timedelta(weeks=i))
            weight_log.append(log)

    # French press
    if language.short_name == 'de':
        exercise = Exercise.objects.get(pk=25)
    else:
        exercise = Exercise.objects.get(pk=84)
    day_set = Set(exerciseday=day, sets=4, order=2)
    day_set.save()
    day_set.exercises.add(exercise)

    setting_list.append(Setting(set=day_set, exercise=exercise, reps=8, order=1))

    # Weight log entries
    for reps in (7, 10):
        for i in range(1, 8):
            log = WorkoutLog(user=user,
                             exercise=exercise,
                             workout=workout,
                             reps=reps,
                             weight=30 - reps + random.randint(1, 4),
                             date=datetime.date.today() - datetime.timedelta(weeks=i))
            weight_log.append(log)

    # Squats
    if language.short_name == 'de':
        exercise = Exercise.objects.get(pk=6)
    else:
        exercise = Exercise.objects.get(pk=111)
    day_set = Set(exerciseday=day, sets=4, order=3)
    day_set.save()
    day_set.exercises.add(exercise)

    setting_list.append(Setting(set=day_set, exercise=exercise, reps=10, order=1))

    # Weight log entries
    for reps in (5, 10, 12):
        for i in range(1, 8):
            log = WorkoutLog(user=user,
                             exercise=exercise,
                             workout=workout,
                             reps=reps,
                             weight=110 - reps + random.randint(1, 10),
                             date=datetime.date.today() - datetime.timedelta(weeks=i))
            weight_log.append(log)

    # Crunches
    if language.short_name == 'de':
        exercise = Exercise.objects.get(pk=4)
    else:
        exercise = Exercise.objects.get(pk=91)
    day_set = Set(exerciseday=day, sets=4, order=4)
    day_set.save()
    day_set.exercises.add(exercise)

    setting_list.append(Setting(set=day_set, exercise=exercise, reps=30, order=1))
    setting_list.append(Setting(set=day_set, exercise=exercise, reps=99, order=2))
    setting_list.append(Setting(set=day_set, exercise=exercise, reps=35, order=3))

    # Leg raises, supersets with crunches
    if language.short_name == 'de':
        exercise = Exercise.objects.get(pk=35)
    else:
        exercise = Exercise.objects.get(pk=126)
    day_set.exercises.add(exercise)

    setting_list.append(Setting(set=day_set, exercise=exercise, reps=30, order=1))
    setting_list.append(Setting(set=day_set, exercise=exercise, reps=40, order=2))
    setting_list.append(Setting(set=day_set, exercise=exercise, reps=99, order=3))

    Setting.objects.bulk_create(setting_list)

    # Save all the log entries
    WorkoutLog.objects.bulk_create(weight_log)

    #
    # (Body) weight entries
    #
    temp = []
    existing_entries = [i.date for i in WeightEntry.objects.filter(user=user)]
    for i in range(1, 20):
        creation_date = datetime.date.today() - datetime.timedelta(days=i)
        if creation_date not in existing_entries:
            entry = WeightEntry(user=user,
                                weight=80 + 0.5 * i + random.randint(1, 3),
                                date=creation_date)
            temp.append(entry)
    WeightEntry.objects.bulk_create(temp)

    #
    # Nutritional plan
    #
    plan = NutritionPlan()
    plan.user = user
    plan.language = language
    plan.description = _('Sample nutrional plan')
    plan.save()

    # Breakfast
    meal = Meal()
    meal.plan = plan
    meal.order = 1
    meal.time = datetime.time(7, 30)
    meal.save()

    # Oatmeal
    if language.short_name == 'de':
        ingredient = Ingredient.objects.get(pk=8197)
    else:
        ingredient = Ingredient.objects.get(pk=2126)

    mealitem = MealItem()
    mealitem.meal = meal
    mealitem.ingredient = ingredient
    mealitem.order = 1
    mealitem.amount = 100
    mealitem.save()

    # Milk
    if language.short_name == 'de':
        ingredient = Ingredient.objects.get(pk=8198)
    else:
        ingredient = Ingredient.objects.get(pk=154)

    mealitem = MealItem()
    mealitem.meal = meal
    mealitem.ingredient = ingredient
    mealitem.order = 2
    mealitem.amount = 100
    mealitem.save()

    # Protein powder
    if language.short_name == 'de':
        ingredient = Ingredient.objects.get(pk=8244)
    else:
        ingredient = Ingredient.objects.get(pk=196)

    mealitem = MealItem()
    mealitem.meal = meal
    mealitem.ingredient = ingredient
    mealitem.order = 3
    mealitem.amount = 30
    mealitem.save()

    #
    # 11 o'clock meal
    meal = Meal()
    meal.plan = plan
    meal.order = 2
    meal.time = datetime.time(11, 0)
    meal.save()

    # Bread, in slices
    if language.short_name == 'de':
        ingredient = Ingredient.objects.get(pk=8225)
        unit = None
        amount = 80
    else:
        ingredient = Ingredient.objects.get(pk=5370)
        unit = IngredientWeightUnit.objects.get(pk=9874)
        amount = 2

    mealitem = MealItem()
    mealitem.meal = meal
    mealitem.ingredient = ingredient
    mealitem.weight_unit = unit
    mealitem.order = 1
    mealitem.amount = amount
    mealitem.save()

    # Turkey
    if language.short_name == 'de':
        ingredient = Ingredient.objects.get(pk=8201)
    else:
        ingredient = Ingredient.objects.get(pk=1643)

    mealitem = MealItem()
    mealitem.meal = meal
    mealitem.order = 2
    mealitem.ingredient = ingredient
    mealitem.amount = 100
    mealitem.save()

    # Cottage cheese
    if language.short_name == 'de':
        ingredient = Ingredient.objects.get(pk=8222)  # TODO: check this!
    else:
        ingredient = Ingredient.objects.get(pk=17)

    mealitem = MealItem()
    mealitem.meal = meal
    mealitem.ingredient = ingredient
    mealitem.order = 3
    mealitem.amount = 50
    mealitem.save()

    # Tomato, one
    if language.short_name == 'de':
        ingredient = Ingredient.objects.get(pk=8217)
        unit = None
        amount = 120
    else:
        ingredient = Ingredient.objects.get(pk=3208)
        unit = IngredientWeightUnit.objects.get(pk=5950)
        amount = 1

    mealitem = MealItem()
    mealitem.meal = meal
    mealitem.weight_unit = unit
    mealitem.ingredient = ingredient
    mealitem.order = 4
    mealitem.amount = amount
    mealitem.save()

    #
    # Lunch (leave empty so users can add their own ingredients)
    meal = Meal()
    meal.plan = plan
    meal.order = 3
    meal.time = datetime.time(13, 0)
    meal.save()

    #
    # Workout schedules
    #

    # create some empty workouts to fill the list
    workout2 = Workout(user=user, comment=_('Placeholder workout nr {0} for schedule').format(1))
    workout2.save()
    workout3 = Workout(user=user, comment=_('Placeholder workout nr {0} for schedule').format(2))
    workout3.save()
    workout4 = Workout(user=user, comment=_('Placeholder workout nr {0} for schedule').format(3))
    workout4.save()

    schedule = Schedule()
    schedule.user = user
    schedule.name = _('My cool workout schedule')
    schedule.start_date = datetime.date.today() - datetime.timedelta(weeks=4)
    schedule.is_active = True
    schedule.is_loop = True
    schedule.save()

    # Add the workouts
    step = ScheduleStep()
    step.schedule = schedule
    step.workout = workout2
    step.duration = 2
    step.order = 1
    step.save()

    step = ScheduleStep()
    step.schedule = schedule
    step.workout = workout
    step.duration = 4
    step.order = 2
    step.save()

    step = ScheduleStep()
    step.schedule = schedule
    step.workout = workout3
    step.duration = 1
    step.order = 3
    step.save()

    step = ScheduleStep()
    step.schedule = schedule
    step.workout = workout4
    step.duration = 6
    step.order = 4
    step.save()

    #
    # Add two more schedules, to make the overview more interesting
    schedule = Schedule()
    schedule.user = user
    schedule.name = _('Empty placeholder schedule')
    schedule.start_date = datetime.date.today() - datetime.timedelta(weeks=15)
    schedule.is_active = False
    schedule.is_loop = False
    schedule.save()

    step = ScheduleStep()
    step.schedule = schedule
    step.workout = workout2
    step.duration = 2
    step.order = 1
    step.save()

    schedule = Schedule()
    schedule.user = user
    schedule.name = _('Empty placeholder schedule')
    schedule.start_date = datetime.date.today() - datetime.timedelta(weeks=30)
    schedule.is_active = False
    schedule.is_loop = False
    schedule.save()

    step = ScheduleStep()
    step.schedule = schedule
    step.workout = workout4
    step.duration = 2
    step.order = 1
    step.save()
