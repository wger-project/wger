# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import datetime

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy

from wger.manager.models import Schedule
from wger.manager.models import ScheduleStep
from wger.manager.models import Workout

from wger.manager.tests.testcase import STATUS_CODES_FAIL
from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class CreateScheduleStepTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a schedule
    '''

    object_class = ScheduleStep
    url = reverse_lazy('step-add', kwargs={'schedule_pk': 1})
    pk = 5
    user_success = 'test'
    user_fail = False
    data = {'workout': 3,
            'duration': 4}


class EditScheduleStepTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a schedule
    '''

    object_class = ScheduleStep
    url = 'step-edit'
    pk = 2
    data = {'workout': 1,
            'duration': 8}
