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

# Third Party
from packaging.version import Version

# Local
from .celery_configuration import app


MIN_APP_VERSION = Version('1.8.0')
"""Minimum version of the mobile app required to access this server"""

MIN_SERVER_VERSION = Version('2.3.0beta1')
"""Minimum version of the server required to run sync commands on this server"""

VERSION = Version('2.3.0beta1')
"""Current version of the app"""


def get_version(version: Version = None) -> str:
    if version is None:
        version = VERSION

    return str(version)
