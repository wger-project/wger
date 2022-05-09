# Django
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


"""
Sets the site URL
"""


class Command(BaseCommand):

    help = 'Sets the site URL from settings.SITE_URL, this is used e.g. for password reset emails'

    def handle(self, *args, **options):

        site = Site.objects.get_current()
        site.domain = settings.SITE_URL
        site.name = settings.SITE_URL
        site.save()
        self.stdout.write(self.style.SUCCESS(f"Set site URL to {settings.SITE_URL}"))
