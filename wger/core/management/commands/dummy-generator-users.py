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
import uuid

# Django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils.text import slugify

# Third Party
from faker import Faker

# wger
from wger.gym.models import (
    Gym,
    GymUserConfig,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy generator for users
    """

    help = 'Dummy generator for users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nr-entries',
            action='store',
            default=20,
            dest='number_users',
            type=int,
            help='The number of users to generate (default: 20)',
        )

        parser.add_argument(
            '--add-to-gym',
            action='store',
            default='auto',
            dest='add_to_gym',
            type=str,
            help='Gym to assign the users to. Allowed values: auto, none, <gym_id>. Default: auto',
        )

    def handle(self, **options):
        faker = Faker()

        self.stdout.write(f'** Generating {options["number_users"]} users')

        match options['add_to_gym']:
            case 'auto':
                gym_list = [gym.pk for gym in Gym.objects.all()]
            case 'none':
                gym_list = []
            case _:
                gym_list = [options['add_to_gym']]

        for i in range(options['number_users']):
            uid = uuid.uuid4()
            first_name = faker.first_name()
            last_name = faker.last_name()

            username = slugify(f'{first_name}, {last_name} - {str(uid).split("-")[1]}')
            email = f'{username}@example.com'
            password = username

            try:
                user = User.objects.create_user(username, email, password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            # Even with the uuid part, usernames are not guaranteed to be unique,
            # in this case, just ignore and continue
            except IntegrityError as e:
                continue

            if gym_list:
                gym_id = random.choice(gym_list)
                user.userprofile.gym_id = gym_id
                user.userprofile.gender = random.choice(['1', '2'])
                user.userprofile.age = random.randint(18, 45)
                user.userprofile.save()

                config = GymUserConfig()
                config.gym_id = gym_id
                config.user = user
                config.save()

            print(f'   - {first_name}, {last_name}')
