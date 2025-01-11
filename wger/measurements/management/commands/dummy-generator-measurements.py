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

# wger
from wger.measurements.models import (
    Category,
    Measurement,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy generator for measurement entries
    """

    help = 'Dummy generator for measurement entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nr-measurements',
            action='store',
            default=40,
            dest='nr_measurements',
            type=int,
            help='The number of measurement entries per category (default: 40)',
        )
        parser.add_argument(
            '--category-id',
            action='store',
            dest='category_id',
            type=int,
            help='Add only to the specified measurement category ID (default: all)',
        )
        parser.add_argument(
            '--user-id',
            action='store',
            dest='user_id',
            type=int,
            help='Add only to the specified user-ID (default: all users)',
        )

    def handle(self, **options):
        self.stdout.write(f'** Generating {options["nr_measurements"]} dummy measurements per user')

        users = (
            [User.objects.get(pk=options['user_id'])] if options['user_id'] else User.objects.all()
        )

        new_entries = []
        for user in users:
            categories = (
                [Category.objects.get(pk=options['category_id'])]
                if options['category_id']
                else Category.objects.filter(user=user)
            )

            self.stdout.write(f'- processing user {user.username}')

            for category in categories:
                base_value = random.randint(10, 100)

                for i in range(options['nr_measurements']):
                    date = datetime.date.today() - datetime.timedelta(days=2 * i)
                    if Measurement.objects.filter(category=category, date=date).exists():
                        continue

                    measurement = Measurement(
                        category=category,
                        value=base_value + 0.5 * i + random.randint(-20, 10),
                        date=date,
                    )
                    new_entries.append(measurement)

        # Bulk-create the entries
        Measurement.objects.bulk_create(new_entries)
