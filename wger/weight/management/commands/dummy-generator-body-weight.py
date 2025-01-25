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
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy generator for weight entries
    """

    help = 'Dummy generator for weight entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nr-entries',
            action='store',
            default=40,
            dest='nr_entries',
            type=int,
            help='The number of measurement entries per category (default: 40)',
        )
        parser.add_argument(
            '--user-id',
            action='store',
            dest='user_id',
            type=int,
            help='Add only to the specified user-ID (default: all users)',
        )

    def handle(self, **options):
        self.stdout.write(f'** Generating {options["nr_entries"]} weight entries per user')

        base_weight = 80

        users = (
            [User.objects.get(pk=options['user_id'])] if options['user_id'] else User.objects.all()
        )

        print(f'** Generating {options["nr_entries"]} weight entries per user')

        for user in users:
            new_entries = []
            self.stdout.write(f'   - generating for {user.username}')

            existing_entries = [i.date for i in WeightEntry.objects.filter(user=user)]

            # Weight entries
            for i in range(options['nr_entries']):
                creation_date = datetime.date.today() - datetime.timedelta(days=i)
                if creation_date not in existing_entries:
                    entry = WeightEntry(
                        user=user,
                        weight=base_weight + 0.5 * i + random.randint(1, 3),
                        date=creation_date,
                    )
                    new_entries.append(entry)

            # Bulk-create the weight entries
            WeightEntry.objects.bulk_create(new_entries)
