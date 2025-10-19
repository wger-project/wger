# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Django
from django.conf import settings
from django.core.management.base import BaseCommand

# wger
from wger.core.api.min_server_version import check_min_server_version
from wger.nutrition.tasks import sync_all_ingredients_task


class Command(BaseCommand):
    help = 'Asynchronously synchronize all ingredients from another wger instance.'

    def handle(self, *args, **options):
        self.stdout.write('Triggering the Celery task to synchronize all ingredients...')

        check_min_server_version(settings.WGER_SETTINGS['WGER_INSTANCE'])

        # Trigger the task asynchronously
        sync_all_ingredients_task.delay()

        self.stdout.write(
            'Synchronization task has been triggered. Check the Celery worker logs for progress.'
        )
