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
import sys

# Django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# wger
from wger.measurements.models import Category


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy generator for measurement categories
    """

    categories = [
        {'name': 'Biceps', 'unit': 'cm'},
        {'name': 'Quads', 'unit': 'cm'},
        {'name': 'Body fat', 'unit': '%'},
        {'name': 'Smartness', 'unit': 'IQ'},
        {'name': 'Hotness', 'unit': '°C'},
        {'name': 'Strength', 'unit': 'KN'},
        {'name': 'Height', 'unit': 'cm'},
        {'name': 'Facebook friends', 'unit': ''},
        {'name': 'Tonnes moved', 'unit': 'T'},
        {'name': 'Weight of my dog', 'unit': 'lb'},
    ]

    help = 'Dummy generator for measurement categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nr-categories',
            action='store',
            default=5,
            dest='nr_categories',
            type=int,
            help='The number of measurement categories to create per user (default: 5, max: 10)',
        )
        parser.add_argument(
            '--user-id',
            action='store',
            dest='user_id',
            type=int,
            help='Add only to the specified user-ID (default: all users)',
        )

    def handle(self, **options):
        self.stdout.write(
            f'** Generating {options["nr_categories"]} dummy measurement categories per user'
        )

        users = (
            [User.objects.get(pk=options['user_id'])] if options['user_id'] else User.objects.all()
        )

        if options['nr_categories'] > 10:
            print(options['nr_categories'])
            print('10 Categories is the maximum allowed')
            sys.exit()

        for user in users:
            self.stdout.write(f'- processing user {user.username}')

            for measurement_cat in random.choices(self.categories, k=options['nr_categories']):
                cat = Category(
                    name=measurement_cat['name'],
                    unit=measurement_cat['unit'],
                    user=user,
                )
                cat.save()
