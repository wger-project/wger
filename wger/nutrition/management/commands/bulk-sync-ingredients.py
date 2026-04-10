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
from django.core.management.base import CommandError

# wger
from wger.core.api.min_server_version import check_min_server_version
from wger.core.management.wger_command import WgerCommand
from wger.nutrition.consts import SyncMode
from wger.nutrition.sync import (
    download_ingredient_dump,
    sync_ingredients_from_dump,
)


class Command(WgerCommand):
    """
    Download a JSONL dump from a wger instance and bulk-import the ingredients.

    This is much faster than the paginated API sync for initial imports or
    full re-syncs of large ingredient databases.
    """

    help = 'Bulk-sync ingredients by downloading a JSONL dump from a wger instance'

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--set-mode',
            action='store',
            default='update',
            dest='mode',
            type=str,
            help=(
                'Script mode, "insert" or "update". Insert will bulk-insert the ingredients as '
                'new entries (fastest, use for empty databases). Update will update existing '
                'entries or create new ones. Default: update'
            ),
        )

        parser.add_argument(
            '--folder',
            action='store',
            default='',
            dest='folder',
            type=str,
            help=(
                'Folder for storing the downloaded dump file. If the file already exists, '
                'it will be reused. Default: use a temporary folder.'
            ),
        )

    def handle(self, **options):
        super().handle(**options)

        remote_url = self.remote_url
        mode = SyncMode.INSERT if options['mode'] == 'insert' else SyncMode.UPDATE

        check_min_server_version(remote_url)

        try:
            file_path = download_ingredient_dump(
                self.stdout.write,
                remote_url=remote_url,
                folder=options['folder'],
                style_fn=self.style.SUCCESS,
            )
        except FileNotFoundError as e:
            raise CommandError(str(e))

        sync_ingredients_from_dump(
            self.stdout.write,
            file_path=file_path,
            mode=mode,
            style_fn=self.style.SUCCESS,
            show_progress_bar=True,
        )
