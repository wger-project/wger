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

MIN_APP_VERSION = Version('2.1.0')
"""
Minimum version of the mobile app required to access this server.

Always use versions in the x.y.z format, without any suffixes like "beta1" or such.
"""

MIN_SERVER_VERSION = Version('2.5.0')
"""Minimum version of the server required to run sync commands on this server"""

VERSION_STRING = '2.7.0'
"""
Current version of the app.

This literal is what the API reports and what .github/workflows/docker.yml
extracts to tag the images, so both agree. It must be valid semver: write
pre-releases as "2.8.0-dev", not "2.8.0.dev0".
"""

VERSION = Version(VERSION_STRING)
"""Parsed form of VERSION_STRING, for version comparisons"""


def get_version() -> str:
    return VERSION_STRING


def get_version_with_git() -> str:
    version = VERSION_STRING
    git_sha1 = os.environ.get('APP_BUILD_COMMIT', '')[:7]
    if git_sha1:
        version += f'+git{git_sha1}'

    return version


def get_version_date() -> str | None:
    return os.environ.get('APP_BUILD_DATE')
