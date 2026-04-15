#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2026 wger Team
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
import os

# Django
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

# Third Party
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Automates the creation of Google OAuth SocialApp credentials'

    def add_arguments(self, parser):
        parser.add_argument('--client_id', type=str, help='Google Client ID')
        parser.add_argument('--client_secret', type=str, help='Google Client Secret')

    def handle(self, *args, **options):
        if not settings.WGER_SETTINGS.get('USE_SOCIAL_AUTH'):
            raise CommandError(
                'Google OAuth is not enabled. '
                'Set WGER_SETTINGS["USE_SOCIAL_AUTH"] = True '
                'in your settings file before running this command.'
            )

        site, created = Site.objects.get_or_create(
            id=1, defaults={'domain': 'localhost:8000', 'name': 'localhost'}
        )

        # Get credentials from arguments or environment variables
        client_id = options['client_id'] or os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = options['client_secret'] or os.environ.get('GOOGLE_CLIENT_SECRET')

        if not client_id or not client_secret:
            self.stderr.write('Error: Missing Client ID or Secret. Provide via args or Env Vars.')
            return

        app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google Auth',
                'client_id': client_id,
                'secret': client_secret,
            },
        )

        # 4. Link the Site to the Social App
        app.sites.add(site)

        status = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(f'Successfully {status} Google OAuth App for {site.domain}')
        )
