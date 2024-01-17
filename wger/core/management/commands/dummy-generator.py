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
from django.core.management import call_command
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
    Dummy generator
    """

    help = (
        'Dummy data generator. This script will call all the individual generator scripts with '
        'some default values. '
    )

    def handle(self, **options):
        call_command('dummy-generator-users')
        call_command('dummy-generator-gyms')
        call_command('dummy-generator-body-weight', '--nr-entries', 100)
        call_command('dummy-generator-nutrition')
        call_command('dummy-generator-measurement-categories')
        call_command('dummy-generator-measurements')
        call_command('dummy-generator-workout-plans')
        call_command('dummy-generator-workout-diary')
