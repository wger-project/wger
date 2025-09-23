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
import logging
import random
from datetime import time

# Django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# wger
from wger.manager.consts import RIR_OPTIONS
from wger.manager.models import (
    Routine,
    WorkoutLog,
    WorkoutSession,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy generator for workout diary entries
    """

    help = 'Dummy generator for workout diary entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            action='store',
            dest='user_id',
            type=int,
            help='Add only to the specified user-ID (default: all users)',
        )

    def handle(self, **options):
        self.stdout.write(f'** Generating dummy workout log entries')

        users = (
            [User.objects.get(pk=options['user_id'])] if options['user_id'] else User.objects.all()
        )

        for user in users:
            self.stdout.write(f'- processing user {user.username}')

            logs = []
            for routine in Routine.objects.filter(user=user):
                for day_data in routine.date_sequence:
                    if day_data.day is None:
                        continue

                    for slot_data in day_data.day.get_slots_gym_mode(day_data.iteration):
                        for exercise_id in slot_data.exercises:
                            for set_data in slot_data.sets:
                                repetitions = (
                                    set_data.repetitions + random.randint(-1, 2)
                                    if set_data.repetitions
                                    else random.randint(3, 12)
                                )
                                weight = (
                                    set_data.weight + random.randint(-4, 10)
                                    if set_data.weight
                                    else random.randint(30, 50)
                                )
                                rir = (
                                    set_data.rir + random.randint(0, 1)
                                    if set_data.rir
                                    else random.choice(RIR_OPTIONS)
                                )

                                rest = (
                                    set_data.rest + random.randint(-10, 40)
                                    if set_data.rest
                                    else random.randint(120, 180)
                                )

                                hour_start = random.randint(8, 20)
                                time_start = time(
                                    hour_start,
                                    random.randint(0, 59),
                                    random.randint(0, 59),
                                )
                                time_end = time(
                                    hour_start + random.randint(1, 3),
                                    random.randint(0, 59),
                                    random.randint(0, 59),
                                )

                                session = WorkoutSession.objects.get_or_create(
                                    user=user,
                                    date=day_data.date,
                                    routine=routine,
                                    defaults={
                                        'impression': random.choice(
                                            [
                                                WorkoutSession.IMPRESSION_GOOD,
                                                WorkoutSession.IMPRESSION_BAD,
                                                WorkoutSession.IMPRESSION_NEUTRAL,
                                            ]
                                        ),
                                        'time_start': time_start,
                                        'time_end': time_end,
                                    },
                                )[0]

                                logs.append(
                                    WorkoutLog(
                                        slot_entry_id=set_data.slot_entry_id,
                                        iteration=day_data.iteration,
                                        user=user,
                                        session=session,
                                        exercise_id=exercise_id,
                                        routine=routine,
                                        repetitions=repetitions,
                                        repetitions_target=set_data.repetitions,
                                        repetitions_unit_id=set_data.repetitions_unit,
                                        weight=weight,
                                        weight_target=set_data.weight,
                                        weight_unit_id=set_data.weight_unit,
                                        date=day_data.date,
                                        rir=rir,
                                        rir_target=set_data.rir,
                                        rest=rest,
                                        rest_target=set_data.rest,
                                    )
                                )

            WorkoutLog.objects.bulk_create(logs)
