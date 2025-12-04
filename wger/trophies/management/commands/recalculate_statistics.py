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

# Standard Library
from datetime import timedelta

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.utils import timezone

# wger
from wger.trophies.services.statistics import UserStatisticsService


class Command(BaseCommand):
    """
    Recalculate user statistics from workout history.

    This command performs a full recalculation of UserStatistics for
    specified users by analyzing their complete workout history.
    """

    help = 'Recalculate user statistics from workout history'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            dest='username',
            help='Username of the user to recalculate statistics for',
        )

        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            default=False,
            help='Recalculate statistics for all users',
        )

        parser.add_argument(
            '--active-only',
            action='store_true',
            dest='active_only',
            default=False,
            help='Only process users who logged in recently (with --all)',
        )

    def handle(self, **options):
        """
        Process the statistics recalculation based on provided options.
        """
        verbosity = int(options['verbosity'])
        username = options['username']
        recalculate_all = options['all']
        active_only = options['active_only']

        # Validate that at least one option is provided
        if not username and not recalculate_all:
            raise CommandError(
                'Please specify --user or --all. See help for details.'
            )

        # Case 1: Recalculate for a specific user
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist')

            if verbosity >= 1:
                self.stdout.write(f'Recalculating statistics for user: {username}')

            stats = UserStatisticsService.update_statistics(user)

            if verbosity >= 2:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✓ Statistics updated:\n'
                        f'  Total workouts: {stats.total_workouts}\n'
                        f'  Total weight lifted: {stats.total_weight_lifted} kg\n'
                        f'  Current streak: {stats.current_streak} days\n'
                        f'  Longest streak: {stats.longest_streak} days\n'
                        f'  Weekend streak: {stats.weekend_workout_streak} weekends'
                    )
                )

            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(f'\nRecalculation complete for {username}')
                )

        # Case 2: Recalculate for all users
        elif recalculate_all:
            # Get users to process
            users = User.objects.all()

            if active_only:
                # Only process users who logged in recently
                inactive_days = settings.WGER_SETTINGS.get('TROPHIES_INACTIVE_USER_DAYS', 30)
                inactive_threshold = timezone.now() - timedelta(days=inactive_days)
                users = users.filter(last_login__gte=inactive_threshold)

                if verbosity >= 1:
                    self.stdout.write(
                        f'Recalculating statistics for active users '
                        f'(logged in within {inactive_days} days)'
                    )
            else:
                if verbosity >= 1:
                    self.stdout.write('Recalculating statistics for all users')

            total_users = users.count()
            processed = 0
            errors = 0

            for user in users:
                try:
                    UserStatisticsService.update_statistics(user)
                    processed += 1

                    if verbosity >= 2:
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Processed: {user.username}')
                        )
                    elif verbosity >= 1 and processed % 100 == 0:
                        self.stdout.write(f'  Processed {processed}/{total_users} users...')

                except Exception as e:
                    errors += 1
                    if verbosity >= 1:
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Error processing {user.username}: {str(e)}'
                            )
                        )

            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nRecalculation complete:\n'
                        f'  Total users: {total_users}\n'
                        f'  Processed: {processed}\n'
                        f'  Errors: {errors}'
                    )
                )
