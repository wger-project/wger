# Django
from django.core.management.base import BaseCommand

# wger
from wger.core.models import User


"""
Custom command permitting users to create user accounts
"""


class Command(BaseCommand):

    help = 'Permit user to create user accounts'

    # Named (optional arguments)
    def add_arguments(self, parser):
        parser.add_argument('name', type=str)

        parser.add_argument(
            '--disable',
            action='store_true',
            dest='disable',
            default=False
        )

    def handle(self, *args, **options):
        name = options['name']

        try:
            user = User.objects.get(username=name)

            if options['disable']:
                user.userprofile.can_add_user = False
                self.stdout.write(self.style.SUCCESS(
                    f"{options['name']} is now DISABLED from adding users via the API"))

            else:
                user.userprofile.can_add_user = True
                self.stdout.write(self.style.SUCCESS(
                    f"{options['name']} is now ALLOWED to add users via the API"))
            user.userprofile.save()

        except Exception as exc:
            self.stdout.write(self.style.WARNING(exc))
