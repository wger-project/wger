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

# Standard Library
import logging
import os

# Third Party
from packaging.version import Version


logger = logging.getLogger(__name__)

# For more details and possibilities, see:
# https://packaging.python.org/en/latest/specifications/version-specifiers/

MIN_APP_VERSION = Version('1.8.0')
"""
Minimum version of the mobile app required to access this server.

Always use versions in the x.y.z format, without any suffixes like "beta1" or such.
"""

MIN_SERVER_VERSION = Version('2.4.0-alpha2')
"""Minimum version of the server required to run sync commands on this server"""

VERSION = Version('2.4.0-alpha3')
"""Current version of the app"""


def get_version(version: Version = None) -> str:
    if version is None:
        version = VERSION

    return str(version)


def get_version_with_git(version: Version = None) -> str:
    version = get_version(version)
    git_sha1 = os.environ.get('APP_BUILD_COMMIT', '')[:7]
    if git_sha1:
        version += f'+git{git_sha1}'

    return version


def get_version_date() -> str | None:
    return os.environ.get('APP_BUILD_DATE')
