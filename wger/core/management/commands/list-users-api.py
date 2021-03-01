# Django
from django.core.management.base import BaseCommand

# wger
from wger.core.models import UserProfile


"""
List users registered via the API
"""


class Command(BaseCommand):

    help = 'List all users registered via REST, grouped by app-user'

    def handle(self, *args, **options):

        for app_profile in UserProfile.objects.filter(can_add_user=True):
            self.stdout.write(self.style.SUCCESS(f"Users created by {app_profile.user.username}:"))

            for user_profile in UserProfile.objects.filter(added_by=app_profile.user):
                self.stdout.write(f"- {user_profile.user.username}")
