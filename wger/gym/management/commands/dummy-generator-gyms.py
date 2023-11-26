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

# Django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker
from faker.providers import DynamicProvider

from wger.gym.models import Gym
# wger
from wger.weight.models import WeightEntry

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy generator for gyms
    """

    help = 'Dummy generator for gyms'

    names_first = [
        "1st",
        "Body",
        "Energy",
        "Granite",
        "Hardcore",
        "Intense",
        "Iron",
        "Muscle",
        "Peak",
        "Power",
        "Pumping",
        "Results",
        "Top",

    ]
    names_second = [
        "Academy",
        "Barbells",
        "Body",
        "Centre",
        "Dumbbells",
        "Factory",
        "Fitness",
        "Force",
        "Gym",
        "Iron",
        "Pit",
        "Team",
        "Workout",
    ]

    def add_arguments(self, parser):

        parser.add_argument(
            '--nr-entries',
            action='store',
            default=10,
            dest='number_gyms',
            type=int,
            help='The number of gyms to generate (default: 10)'
        )

    def handle(self, **options):
        gym_names_1 = DynamicProvider(
            provider_name="gym_names",
            elements=self.names_first,
        )

        gym_names_2 = DynamicProvider(
            provider_name="gym_names2",
            elements=self.names_second
        )

        faker = Faker()
        faker.add_provider(gym_names_1)
        faker.add_provider(gym_names_2)

        self.stdout.write(f"** Generating {options['number_gyms']} gyms")

        gym_list = []
        for i in range(1, options['number_gyms']):
            found = False
            while not found:
                part1 = faker.gym_names()
                part2 = faker.gym_names2()

                # We don't want names like "Iron Iron"
                if part1 != part2:
                    found = True

            name = f"{part1} {part2}"
            gym = Gym()
            gym.name = name
            gym_list.append(gym)

            self.stdout.write('   - {0}'.format(gym.name))

        # Bulk-create the entries
        Gym.objects.bulk_create(gym_list)
