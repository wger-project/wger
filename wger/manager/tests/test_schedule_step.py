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
from django.urls import reverse_lazy

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
)
from wger.manager.models import ScheduleStep


class ScheduleStepRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(str(ScheduleStep.objects.get(pk=1)), 'A test workout')


class ScheduleStepTestCase(WgerTestCase):
    """
    Other tests
    """

    def test_schedule_dates_util(self, fail=False):
        """
        Test the get_dates() method
        """
        s1 = ScheduleStep.objects.get(pk=1)
        s2 = ScheduleStep.objects.get(pk=2)
        s3 = ScheduleStep.objects.get(pk=3)

        self.assertEqual(s1.get_dates(), (datetime.date(2013, 4, 21), datetime.date(2013, 5, 12)))
        self.assertEqual(s2.get_dates(), (datetime.date(2013, 5, 12), datetime.date(2013, 6, 16)))
        self.assertEqual(s3.get_dates(), (datetime.date(2013, 6, 16), datetime.date(2013, 6, 30)))


class CreateScheduleStepTestCase(WgerAddTestCase):
    """
    Tests adding a schedule
    """

    object_class = ScheduleStep
    url = reverse_lazy('manager:step:add', kwargs={'schedule_pk': 1})
    user_success = 'test'
    user_fail = False
    data = {'workout': 3, 'duration': 4}


class EditScheduleStepTestCase(WgerEditTestCase):
    """
    Tests editing a schedule
    """

    object_class = ScheduleStep
    url = 'manager:step:edit'
    pk = 2
    data = {'workout': 1, 'duration': 8}


class DeleteScheduleStepTestCase(WgerDeleteTestCase):
    """
    Tests editing a schedule
    """

    object_class = ScheduleStep
    url = 'manager:step:delete'
    pk = 2


class ScheduleStepApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the schedule step overview resource
    """

    pk = 4
    resource = ScheduleStep
    private_resource = True
    data = {
        'workout': '3',
        'schedule': '1',
        'duration': '8',
    }
