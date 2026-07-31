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

# Django
from django.utils import timezone

# wger
from wger.core.tests import api_base_test
from wger.manager.models import WorkoutSession


class WorkoutSessionApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the workout overview resource
    """

    pk = 'bbbbbbbb-bbbb-bbbb-bbbb-000000000005'
    resource = WorkoutSession
    private_resource = True
    data = {
        'routine': 3,
        'notes': 'My new insights',
        'impression': '3',
        'datetime_start': timezone.make_aware(datetime.datetime(2014, 1, 25, 10, 0)),
        'datetime_end': timezone.make_aware(datetime.datetime(2014, 1, 25, 13, 0)),
    }
