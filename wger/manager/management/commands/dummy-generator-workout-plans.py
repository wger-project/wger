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

# Django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# wger
from wger.core.models import DaysOfWeek
from wger.exercises.models import Exercise
from wger.manager.models import (
    Day,
    Set,
    Setting,
    Workout,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy generator for workout plans
    """

    help = 'Dummy generator for workout plans'

    def add_arguments(self, parser):
        parser.add_argument(
            '--plans',
            action='store',
            default=10,
            dest='nr_plans',
            type=int,
            help='The number of workout plans to create per user (default: 10)',
        )
        parser.add_argument(
            '--user-id',
            action='store',
            dest='user_id',
            type=int,
            help='Add only to the specified user-ID (default: all users)',
        )

    def handle(self, **options):
        self.stdout.write(f'** Generating {options["nr_plans"]} dummy workout plan(s) per user')

        users = (
            [User.objects.get(pk=options['user_id'])] if options['user_id'] else User.objects.all()
        )

        for user in users:
            self.stdout.write(f'- processing user {user.username}')

            # Add plan
            for _ in range(options['nr_plans']):
                uid = str(uuid.uuid4()).split('-')
                start_date = datetime.date.today() - datetime.timedelta(days=random.randint(0, 100))
                workout = Workout(
                    user=user,
                    name=f'Dummy workout - {uid[1]}',
                    creation_date=start_date,
                )
                workout.save()

                # Select a random number of workout days
                nr_of_days = random.randint(1, 5)
                day_list = [i for i in range(1, 8)]
                random.shuffle(day_list)

                # Load all exercises to a list
                exercise_list = [i for i in Exercise.objects.filter(language_id=2)]

                for day in day_list[0:nr_of_days]:
                    uid = str(uuid.uuid4()).split('-')
                    weekday = DaysOfWeek.objects.get(pk=day)

                    day = Day(
                        training=workout,
                        description=f'Dummy day - {uid[0]}',
                    )
                    day.save()
                    day.day.add(weekday)

                    # Select a random number of exercises
                    nr_of_exercises = random.randint(3, 10)
                    random.shuffle(exercise_list)
                    day_exercises = exercise_list[0:nr_of_exercises]
                    order = 1
                    for exercise in day_exercises:
                        reps = random.choice([1, 3, 5, 8, 10, 12, 15])
                        sets = random.randint(2, 4)

                        day_set = Set(
                            exerciseday=day,
                            sets=sets,
                            order=order,
                        )
                        day_set.save()

                        setting = Setting(
                            set=day_set,
                            exercise_base=exercise.exercise_base,
                            reps=reps,
                            order=order,
                        )
                        setting.save()
                        order += 1
