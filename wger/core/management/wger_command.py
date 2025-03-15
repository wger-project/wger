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
from django.core.exceptions import ValidationError
from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.core.validators import URLValidator

# wger
from wger.core.api.min_server_version import check_min_server_version


class WgerCommand(BaseCommand):
    """
    Base class for all wger commands that allows to set the remote URL
    """

    remote_url = settings.WGER_SETTINGS['WGER_INSTANCE']

    def add_arguments(self, parser):
        parser.add_argument(
            '--remote-url',
            action='store',
            dest='remote_url',
            default=settings.WGER_SETTINGS['WGER_INSTANCE'],
            help=f'Remote URL to fetch the ingredients from (default: WGER_SETTINGS'
            f'["WGER_INSTANCE"] - {settings.WGER_SETTINGS["WGER_INSTANCE"]})',
        )

    def handle(self, **options):
        remote_url = options['remote_url']

        try:
            val = URLValidator()
            val(remote_url)
            self.remote_url = remote_url
        except ValidationError:
            raise CommandError(f'"{remote_url}" is not a valid URL, please enter a valid one')

        check_min_server_version(remote_url)
