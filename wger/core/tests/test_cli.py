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
import tempfile
from unittest import mock

# Django
from django.test import SimpleTestCase

# Third Party
from invoke import Config

# wger
from wger.tasks import WgerConfig


class WgerConfigTestCase(SimpleTestCase):
    """
    Test the invoke configuration used by the CLI
    """

    def test_user_config_file_is_ignored(self):
        with tempfile.TemporaryDirectory() as home:
            with open(os.path.join(home, '.invoke.yaml'), 'w') as config_file:
                config_file.write('run:\n  echo: true\n')

            with mock.patch.dict(os.environ, {'HOME': home}):
                # Sanity check, invoke's own config does read the file
                self.assertTrue(Config().run.echo)

                self.assertFalse(WgerConfig().run.echo)
