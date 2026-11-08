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
import os
import re
from unittest import mock

# Django
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.version import (
    VERSION_STRING,
    get_version_with_git,
)


SEMVER = re.compile(r'^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$')


class VersionTestCase(WgerTestCase):
    """
    Tests the version constants and the version endpoint
    """

    def test_version_string_is_semver(self):
        """
        The literal is used as-is as a docker tag, which only accepts semver
        """
        self.assertRegex(VERSION_STRING, SEMVER)

    def test_endpoint_reports_the_literal(self):
        """
        The API answers with the literal, not with the PEP 440 normalisation
        """
        response = self.client.get(reverse('app_version'))
        self.assertEqual(response.json(), VERSION_STRING)

    def test_git_sha_is_appended_as_build_metadata(self):
        """
        The build commit is appended in the semver build metadata syntax
        """
        with mock.patch.dict(os.environ, {'APP_BUILD_COMMIT': 'abcdef1234567890'}):
            self.assertEqual(get_version_with_git(), f'{VERSION_STRING}+gitabcdef1')
