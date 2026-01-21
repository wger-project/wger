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
from wger.core.tests.base_testcase import WgerAccessTestCase


logger = logging.getLogger(__name__)


class TrophiesOverviewTestCase(WgerAccessTestCase):
    """
    Test case for the trophies overview page
    """

    url = 'trophies:admin-overview'
    anonymous_fail = True
    user_success = 'admin'
    user_fail = (
        'manager1',
        'manager2',
        'general_manager1',
        'manager3',
        'manager4',
        'test',
        'member1',
        'member2',
        'member3',
        'member4',
        'member5',
    )
