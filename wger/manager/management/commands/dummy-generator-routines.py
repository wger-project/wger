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
from wger.exercises.models import Exercise
from wger.manager.models import (
    Day,
    RepsConfig,
    Routine,
    SetsConfig,
    Slot,
    SlotEntry,
    WeightConfig,
)
from wger.manager.models.abstract_config import OperationChoices


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy generator for routines
    """

    help = 'Dummy generator for routines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--routines',
            action='store',
            default=10,
            dest='nr_plans',
            type=int,
            help='The number of routines to create per user (default: 10)',
        )
        parser.add_argument(
            '--user-id',
            action='store',
            dest='user_id',
            type=int,
            help='Add only to the specified user-ID (default: all users)',
        )

    def handle(self, **options):
        self.stdout.write(f"** Generating {options['nr_plans']} dummy routine(s) per user")

        users = (
            [User.objects.get(pk=options['user_id'])] if options['user_id'] else User.objects.all()
        )

        for user in users:
            self.stdout.write(f'- processing user {user.username}')

            # Add plan
            for _ in range(options['nr_plans']):
                uid = str(uuid.uuid4()).split('-')
                start_date = datetime.date.today() - datetime.timedelta(days=random.randint(0, 100))

                routine = Routine(
                    user=user,
                    name=f'Dummy routine - {uid[0]}',
                    start=start_date,
                    end=start_date + datetime.timedelta(weeks=6),
                )
                routine.save()

                # Select a random number of days and juggle them till they are all connected
                nr_of_days = random.randint(2, 5)

                day_list = []
                for i in range(nr_of_days):
                    uid = str(uuid.uuid4()).split('-')
                    day = Day(routine=routine, name=f'Dummy day - {uid[0]}', order=i)
                    day.save()
                    day_list.append(day)

                # Add exercises (no supersets, all very simple)
                exercise_list = [i for i in Exercise.objects.all()]
                for day in day_list:
                    nr_of_exercises = random.randint(3, 6)
                    exercises = random.choices(exercise_list, k=nr_of_exercises)
                    order = 1
                    for exercise in exercises:
                        slot = Slot(day=day, order=order)
                        slot.save()
                        order += 1

                        slot_entry = SlotEntry(exercise=exercise, order=order, slot=slot)
                        slot_entry.save()

                        reps = random.choice([1, 3, 5, 8, 10, 12, 15])
                        sets = random.randint(2, 4)
                        weight = random.randint(20, 100)

                        SetsConfig(
                            slot_entry=slot_entry,
                            value=sets,
                            iteration=1,
                            operation=OperationChoices.REPLACE,
                        ).save()

                        RepsConfig(
                            slot_entry=slot_entry,
                            value=reps,
                            iteration=1,
                            operation=OperationChoices.REPLACE,
                        ).save()

                        WeightConfig(
                            slot_entry=slot_entry,
                            value=weight,
                            iteration=1,
                            operation=OperationChoices.REPLACE,
                        ).save()
