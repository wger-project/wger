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

# Standard Library
import datetime
import logging
import random
import uuid
from random import (
    choice,
    randint,
)
from uuid import uuid4

# Django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

# wger
from wger.core.models import (
    DaysOfWeek,
    Language,
)
from wger.exercises.models import Exercise
from wger.manager.models import (
    Day,
    Set,
    Setting,
    Workout,
    WorkoutLog,
)
from wger.nutrition.models import (
    Ingredient,
    LogItem,
    Meal,
    MealItem,
    NutritionPlan,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy generator for workout diary entries
    """

    help = 'Dummy generator for workout diary entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--diary-entries',
            action='store',
            default=30,
            dest='nr_diary_entries',
            type=int,
            help='The number of workout logs to create per day (default: 30)',
        )
        parser.add_argument(
            '--user-id',
            action='store',
            dest='user_id',
            type=int,
            help='Add only to the specified user-ID (default: all users)',
        )

    def handle(self, **options):
        self.stdout.write(f'** Generating {options["nr_diary_entries"]} dummy diary entries')

        users = (
            [User.objects.get(pk=options['user_id'])] if options['user_id'] else User.objects.all()
        )

        weight_log = []
        for user in users:
            self.stdout.write(f'- processing user {user.username}')

            # Create a log for each workout day, set, setting, reps, weight, date
            for workout in Workout.objects.filter(user=user):
                for day in workout.day_set.all():
                    for workout_set in day.set_set.all():
                        for setting in workout_set.setting_set.all():
                            for reps in (8, 10, 12):
                                for i in range(options['nr_diary_entries']):
                                    date = datetime.date.today() - datetime.timedelta(weeks=i)
                                    log = WorkoutLog(
                                        user=user,
                                        exercise_base=setting.exercise_base,
                                        workout=workout,
                                        reps=reps,
                                        weight=50 - reps + random.randint(1, 10),
                                        date=date,
                                    )
                                    weight_log.append(log)

        # Bulk-create the logs
        WorkoutLog.objects.bulk_create(weight_log)
