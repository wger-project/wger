# Standard Library
from urllib.parse import urlparse

# Django
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.core.validators import URLValidator


"""
Sets the site URL
"""


class Command(BaseCommand):
    help = 'Sets the site URL from settings.SITE_URL, this is used e.g. for password reset emails'

    def handle(self, *args, **options):
        if not settings.SITE_URL:
            return

        try:
            val = URLValidator()
            val(settings.SITE_URL)
        except ValidationError:
            raise CommandError('Please set a valid URL for SITE_URL')

        domain = urlparse(settings.SITE_URL).netloc
        site = Site.objects.get_current()
        site.domain = domain
        site.name = settings.SITE_URL
        site.save()
        self.stdout.write(self.style.SUCCESS(f'Set site URL to {domain}'))
