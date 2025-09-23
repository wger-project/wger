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
from wger.manager.models import WorkoutSession


class WorkoutSessionApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the workout overview resource
    """

    pk = 5
    resource = WorkoutSession
    private_resource = True
    data = {
        'workout': 3,
        'date': datetime.date(2014, 1, 25),
        'notes': 'My new insights',
        'impression': '3',
        'time_start': datetime.time(10, 0),
        'time_end': datetime.time(13, 0),
    }
