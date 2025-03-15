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

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.dataclasses import ConfigRequirements
from wger.manager.models import SetsConfig


logger = logging.getLogger(__name__)


class ChangeConfigTestCase(WgerTestCase):
    """
    Test some logic in the AbstractChangeConfig model
    (here with a SetsConfig since the abstract class cannot be instantiated)
    """

    def test_requirements_session(self):
        """
        Test the ConfigRequirements object is successfully created
        """

        config = SetsConfig(requirements={'rules': ['weight', 'repetitions']})

        self.assertEqual(
            config.requirements_object,
            ConfigRequirements(data={'rules': ['weight', 'repetitions']}),
        )

    def test_bool_false(self):
        """
        Test the __bool__ method in ConfigRequirements
        """

        config = SetsConfig.objects.get(pk=1)

        self.assertEqual(config.requirements, {'rules': []})
        self.assertFalse(config.requirements_object)

    def test_bool_true(self):
        """
        Test the __bool__ method in ConfigRequirements
        """

        config = SetsConfig.objects.get(pk=1)
        config.requirements = {'rules': ['weight', 'repetitions']}

        self.assertTrue(config.requirements_object)
