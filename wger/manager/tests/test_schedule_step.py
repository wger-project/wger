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

from django.core.urlresolvers import reverse_lazy

from wger.core.tests import api_base_test
from wger.manager.models import ScheduleStep
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class CreateScheduleStepTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a schedule
    '''

    object_class = ScheduleStep
    url = reverse_lazy('manager:step:add', kwargs={'schedule_pk': 1})
    user_success = 'test'
    user_fail = False
    data = {'workout': 3,
            'duration': 4}


class EditScheduleStepTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a schedule
    '''

    object_class = ScheduleStep
    url = 'manager:step:edit'
    pk = 2
    data = {'workout': 1,
            'duration': 8}


class DeleteScheduleStepTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests editing a schedule
    '''

    object_class = ScheduleStep
    url = 'manager:step:delete'
    pk = 2


class ScheduleStepApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the schedule step overview resource
    '''
    pk = 4
    resource = ScheduleStep
    private_resource = True
    data = {'workout': '3',
            'schedule': '1',
            'duration': '8'}
