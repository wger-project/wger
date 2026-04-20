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


if settings.WGER_SETTINGS.get('USE_SOCIAL_AUTH', False):
    # Third Party
    from allauth.socialaccount.models import SocialApp


SUPPORTED_PROVIDERS = ('google', 'github', 'facebook')

ENV_KEY_MAP = {
    'google': ('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'),
}

PROVIDER_DISPLAY_NAMES = {
    'google': 'Google Auth',
    'github': 'GitHub Auth',
    'facebook': 'Facebook Auth',
}


class Command(BaseCommand):
    """
    Management command to create or update a SocialApp (allauth) for a Google OAuth provider.

    This command seeds the single database record that allauth requires to perform
    Google OAuth2 authentication. Run it once after initial deployment, or whenever
    your Google OAuth credentials change.

    NOTE: To perform full CRUD management of SocialApp records (listing all apps, deleting
    a provider, or editing individual fields), use the Django admin interface. Enable the admin
    in settings_global.py and add '/admin' to urls.py.

    Usage:
        python3 manage.py setup_social_oauth \\
            --provider "google" \\
            --client_id "YOUR_GOOGLE_CLIENT_ID" \\
            --client_secret "YOUR_GOOGLE_CLIENT_SECRET" \\
            --domain localhost:8000

    Google Cloud Console setup:
        1. Go to APIs & Services → Credentials → Create OAuth 2.0 Client ID
        2. Application type: Web application
        3. Authorized redirect URI: http://YOUR_DOMAIN/accounts/google/login/callback/
        4. Copy the client ID and secret, then run this command.
    """

    help = 'Creates or updates allauth SocialApp credentials for Google'

    def add_arguments(self, parser):
        parser.add_argument(
            '--provider',
            type=str,
            required=True,
            choices=SUPPORTED_PROVIDERS,
            help='OAuth provider name: google',
        )
        parser.add_argument('--client_id', type=str, help='Oauth App Client ID')
        parser.add_argument('--client_secret', type=str, help='Oauth App Client Secret')
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost:8000',
            help='Site domain (default: localhost:8000)',
        )

    def handle(self, *args, **options):
        if not settings.WGER_SETTINGS.get('USE_SOCIAL_AUTH', False):
            raise CommandError(
                'Google OAuth is not enabled. '
                'Set WGER_SETTINGS["USE_SOCIAL_AUTH"] = True '
                'in your settings file before running this command.'
            )

        provider = options['provider']
        env_id_key, env_secret_key = ENV_KEY_MAP[provider]

        client_id = options['client_id'] or os.environ.get(env_id_key)
        client_secret = options['client_secret'] or os.environ.get(env_secret_key)

        if not client_id or not client_secret:
            self.stderr.write(
                f'Error: Missing credentials for {provider}. '
                f'Pass --client_id / --client_secret or set '
                f'{env_id_key} / {env_secret_key} env variables.'
            )
            return

        domain = options['domain']

        app, created = SocialApp.objects.get_or_create(
            provider=provider,
            defaults={
                'name': PROVIDER_DISPLAY_NAMES[provider],
                'client_id': client_id,
                'secret': client_secret,
            },
        )
        if not created:
            # Update existing record
            app.client_id = client_id
            app.secret = client_secret
            app.save()

        # Link the Site to the Social App

        site, _ = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': domain})
        app.sites.add(site)

        status = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(
                f'{status} {PROVIDER_DISPLAY_NAMES[provider]} OAuth App for {site.domain}'
            )
        )
