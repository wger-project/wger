import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Automates the creation of Google OAuth SocialApp credentials'

    def add_arguments(self, parser):
        parser.add_argument('--client_id', type=str, help='Google Client ID')
        parser.add_argument('--client_secret', type=str, help='Google Client Secret')

    def handle(self, *args, **options):
        # 1. Get or Create the Site (usually ID 1 for localhost)
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={'domain': 'localhost:8000', 'name': 'localhost'}
        )

        # 2. Get credentials from arguments or environment variables
        client_id = options['client_id'] or os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = options['client_secret'] or os.environ.get('GOOGLE_CLIENT_SECRET')

        if not client_id or not client_secret:
            self.stderr.write("Error: Missing Client ID or Secret. Provide via args or Env Vars.")
            return

        # 3. Create or Update the Social App
        app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google Auth',
                'client_id': client_id,
                'secret': client_secret,
            }
        )

        # 4. Link the Site to the Social App
        app.sites.add(site)

        status = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f'Successfully {status} Google OAuth App for {site.domain}'))
        