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
import logging

# wger
from wger.core.tests import api_base_test
from wger.manager.models import WorkoutLog


logger = logging.getLogger(__name__)


class WorkoutLogApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the workout log overview resource
    """

    pk = 5
    resource = WorkoutLog
    private_resource = True
    data = {
        'exercise': 1,
        'routine': 3,
        'repetitions': 3,
        'repetitions_unit': 1,
        'weight_unit': 2,
        'weight': 2,
        'date': datetime.date.today(),
    }
