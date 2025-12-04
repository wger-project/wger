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
from django.contrib.auth.models import User
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

# wger
from wger.trophies.models import Trophy
from wger.trophies.services.trophy import TrophyService


class Command(BaseCommand):
    """
    Manually trigger trophy evaluation for users.

    This command allows administrators to evaluate trophies for specific
    users, specific trophies, or all trophies for all users.
    """

    help = 'Evaluate trophies for users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            dest='username',
            help='Username of the user to evaluate trophies for',
        )

        parser.add_argument(
            '--trophy',
            type=int,
            dest='trophy_id',
            help='ID of a specific trophy to evaluate',
        )

        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            default=False,
            help='Evaluate all trophies for all active users',
        )

        parser.add_argument(
            '--force-reevaluate',
            action='store_true',
            dest='force_reevaluate',
            default=False,
            help='Re-evaluate all trophies, including already earned ones',
        )

    def handle(self, **options):
        """
        Process the trophy evaluation based on provided options.
        """
        verbosity = int(options['verbosity'])
        username = options['username']
        trophy_id = options['trophy_id']
        evaluate_all = options['all']
        force_reevaluate = options['force_reevaluate']

        # Validate that at least one option is provided
        if not username and not trophy_id and not evaluate_all:
            raise CommandError(
                'Please specify --user, --trophy, or --all. See help for details.'
            )

        # Case 1: Evaluate for a specific user
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist')

            if verbosity >= 1:
                self.stdout.write(f'Evaluating trophies for user: {username}')

            awarded = TrophyService.evaluate_all_trophies(user)

            if verbosity >= 2:
                for user_trophy in awarded:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Awarded trophy "{user_trophy.trophy.name}" to {username}'
                        )
                    )

            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nEvaluation complete: {len(awarded)} trophy(ies) awarded'
                    )
                )

        # Case 2: Evaluate a specific trophy for all users (or force re-evaluation)
        elif trophy_id or evaluate_all or force_reevaluate:
            trophy_ids = None
            if trophy_id:
                # Validate trophy exists
                try:
                    trophy = Trophy.objects.get(id=trophy_id)
                    trophy_ids = [trophy_id]

                    if verbosity >= 1:
                        self.stdout.write(
                            f'Evaluating trophy "{trophy.name}" for all users'
                        )
                except Trophy.DoesNotExist:
                    raise CommandError(f'Trophy with ID {trophy_id} does not exist')
            else:
                if verbosity >= 1:
                    self.stdout.write('Evaluating all trophies for all users')

            # Use the reevaluate service method
            results = TrophyService.reevaluate_trophies(
                trophy_ids=trophy_ids,
                user_ids=None,  # All active users
            )

            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nEvaluation complete:\n'
                        f'  Users checked: {results["users_checked"]}\n'
                        f'  Trophies awarded: {results["trophies_awarded"]}'
                    )
                )

        # Case 3: Force re-evaluation (handled above)
        # The force_reevaluate flag is implicit in using reevaluate_trophies method
