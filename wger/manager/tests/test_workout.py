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
import datetime

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import Workout


class WorkoutModelTestCase(WgerTestCase):
    """
    Tests other functionality from the model
    """

    def test_unicode(self):
        """
        Test the unicode representation
        """

        workout = Workout()
        workout.creation_date = datetime.date.today()
        self.assertEqual(
            str(workout),
            f'Workout ({datetime.date.today()})',
        )

        workout.name = 'my description'
        self.assertEqual(str(workout), 'my description')


class WorkoutApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the workout overview resource
    """

    pk = 3
    resource = Workout
    private_resource = True
    data = {'name': 'A new comment'}
