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

# wger
from wger.core.management.wger_command import WgerCommand
from wger.exercises.sync import (
    handle_deleted_entries,
    sync_categories,
    sync_equipment,
    sync_exercises,
    sync_languages,
    sync_licenses,
    sync_muscles,
)


class Command(WgerCommand):
    """
    Synchronizes exercise data from a wger instance to the local database
    """

    remote_url = settings.WGER_SETTINGS['WGER_INSTANCE']

    help = """Synchronizes exercise data from a wger instance to the local database.
            This script also deletes entries that were removed on the server such
            as exercises, images or videos.

            Please note that at the moment the following objects can only identified
            by their id. If you added new objects they might have the same IDs as the
            remote ones and will be overwritten:
            - categories
            - muscles
            - equipment
            """

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--dont-delete',
            action='store_true',
            dest='skip_delete',
            default=False,
            help='Skips deleting any entries',
        )

    def handle(self, **options):
        super().handle(**options)

        # Process everything
        sync_languages(self.stdout.write, self.remote_url, self.style.SUCCESS)
        sync_categories(self.stdout.write, self.remote_url, self.style.SUCCESS)
        sync_muscles(self.stdout.write, self.remote_url, self.style.SUCCESS)
        sync_equipment(self.stdout.write, self.remote_url, self.style.SUCCESS)
        sync_licenses(self.stdout.write, self.remote_url, self.style.SUCCESS)
        sync_exercises(self.stdout.write, self.remote_url, self.style.SUCCESS)
        if not options['skip_delete']:
            handle_deleted_entries(self.stdout.write, self.remote_url, self.style.SUCCESS)
