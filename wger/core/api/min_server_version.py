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
from django.core.management import CommandError

# Third Party
import requests
from packaging.version import parse

# wger
from wger.core.api.endpoints import MIN_SERVER_VERSION_ENDPOINT
from wger.utils.url import make_uri
from wger.version import VERSION


def check_min_server_version(remote_url):
    url = make_uri(MIN_SERVER_VERSION_ENDPOINT, server_url=remote_url)
    min_version = parse(requests.get(url).json())

    if min_version > VERSION:
        raise CommandError(
            f'The remote wger server at {remote_url} requires at least version {min_version}, '
            f'but this instance is running version {VERSION}. Please update to continue.'
        )
