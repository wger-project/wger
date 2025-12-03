#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Django
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

# wger
from wger.trophies.models import Trophy


class Command(BaseCommand):
    """
    Load initial trophy definitions into the database.

    This command is idempotent - it can be run multiple times safely.
    Existing trophies with the same name will be updated, not duplicated.
    """

    help = 'Load initial trophy definitions into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help='Update existing trophies if they already exist',
        )

    def handle(self, **options):
        """
        Load the initial trophy definitions.
        """
        verbosity = int(options['verbosity'])
        update_existing = options['update']

        # Define the initial trophies
        trophies_data = [
            {
                'name': _('Beginner'),
                'description': _('Complete your first workout'),
                'trophy_type': Trophy.TYPE_COUNT,
                'checker_class': 'count_based',
                'checker_params': {'count': 1},
                'is_hidden': False,
                'is_progressive': False,
                'order': 1,
            },
            {
                'name': _('Unstoppable'),
                'description': _('Maintain a 30-day workout streak'),
                'trophy_type': Trophy.TYPE_SEQUENCE,
                'checker_class': 'streak',
                'checker_params': {'days': 30},
                'is_hidden': False,
                'is_progressive': True,
                'order': 2,
            },
            {
                'name': _('Weekend Warrior'),
                'description': _('Work out on Saturday and Sunday for 4 consecutive weekends'),
                'trophy_type': Trophy.TYPE_SEQUENCE,
                'checker_class': 'weekend_warrior',
                'checker_params': {'weekends': 4},
                'is_hidden': False,
                'is_progressive': True,
                'order': 3,
            },
            {
                'name': _('Lifter'),
                'description': _('Lift a cumulative total of 5,000 kg'),
                'trophy_type': Trophy.TYPE_VOLUME,
                'checker_class': 'volume',
                'checker_params': {'kg': 5000},
                'is_hidden': False,
                'is_progressive': True,
                'order': 4,
            },
            {
                'name': _('Atlas'),
                'description': _('Lift a cumulative total of 100,000 kg'),
                'trophy_type': Trophy.TYPE_VOLUME,
                'checker_class': 'volume',
                'checker_params': {'kg': 100000},
                'is_hidden': False,
                'is_progressive': True,
                'order': 5,
            },
            {
                'name': _('Early Bird'),
                'description': _('Complete a workout before 6:00 AM'),
                'trophy_type': Trophy.TYPE_TIME,
                'checker_class': 'time_based',
                'checker_params': {'before': '06:00'},
                'is_hidden': False,
                'is_progressive': False,
                'order': 6,
            },
            {
                'name': _('Night Owl'),
                'description': _('Complete a workout after 9:00 PM'),
                'trophy_type': Trophy.TYPE_TIME,
                'checker_class': 'time_based',
                'checker_params': {'after': '21:00'},
                'is_hidden': False,
                'is_progressive': False,
                'order': 7,
            },
            {
                'name': _('New Year, New Me'),
                'description': _('Work out on January 1st'),
                'trophy_type': Trophy.TYPE_DATE,
                'checker_class': 'date_based',
                'checker_params': {'month': 1, 'day': 1},
                'is_hidden': False,
                'is_progressive': False,
                'order': 8,
            },
            {
                'name': _('Phoenix'),
                'description': _('Return to training after being inactive for 30 days'),
                'trophy_type': Trophy.TYPE_OTHER,
                'checker_class': 'inactivity_return',
                'checker_params': {'inactive_days': 30},
                'is_hidden': True,
                'is_progressive': False,
                'order': 9,
            },
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for trophy_data in trophies_data:
            # Convert lazy translation to string for database lookup
            name = str(trophy_data['name'])

            # Check if trophy already exists
            existing = Trophy.objects.filter(name=name).first()

            if existing:
                if update_existing:
                    # Update existing trophy
                    for key, value in trophy_data.items():
                        if key != 'name':  # Don't update the name
                            setattr(existing, key, value)
                    existing.save()
                    updated_count += 1

                    if verbosity >= 2:
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Updated trophy: {name}')
                        )
                else:
                    skipped_count += 1

                    if verbosity >= 2:
                        self.stdout.write(
                            self.style.WARNING(f'- Skipped existing trophy: {name}')
                        )
            else:
                # Create new trophy
                Trophy.objects.create(**trophy_data)
                created_count += 1

                if verbosity >= 2:
                    self.stdout.write(
                        self.style.SUCCESS(f'+ Created trophy: {name}')
                    )

        # Summary
        if verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nTrophy loading complete:\n'
                    f'  Created: {created_count}\n'
                    f'  Updated: {updated_count}\n'
                    f'  Skipped: {skipped_count}\n'
                    f'  Total: {len(trophies_data)}'
                )
            )
