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

# wger
from wger.core.api.min_server_version import check_min_server_version
from wger.core.management.wger_command import WgerCommand
from wger.nutrition.sync import sync_ingredients


class Command(WgerCommand):
    """
    Synchronizes ingredient data from a wger instance to the local database
    """

    help = """Synchronizes ingredient data from a wger instance to the local database"""

    def handle(self, **options):
        super().handle(**options)

        remote_url = options['remote_url']
        check_min_server_version(remote_url)

        sync_ingredients(self.stdout.write, self.remote_url, self.style.SUCCESS)
